#!/usr/bin/env python3
"""Check hexagonal architecture boundaries in the Mano platform.

Ensures proper separation between domain, application, infrastructure,
and web layers according to hexagonal architecture principles.
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

# Constants for complexity checking
MAX_NESTING_LEVEL = 4
MAX_FUNCTION_LENGTH = 50
MIN_ARGS_FOR_HELP = 2

# Define allowed imports for each layer
LAYER_RULES = {
    "domain": {
        "allowed_internal": {"domain"},
        "forbidden_internal": {"application", "infrastructure", "web"},
        "forbidden_external": {
            "fastapi",
            "sqlalchemy",
            "asyncpg",
            "redis",
            "httpx",
            "uvicorn",
            "pydantic",
            "jose",
            "structlog",
        },
    },
    "application": {
        "allowed_internal": {"domain", "application"},
        "forbidden_internal": {"infrastructure", "web"},
        "forbidden_external": {
            "sqlalchemy",
            "asyncpg",
            "redis",
            "fastapi.responses",
            "uvicorn",
            "jose",
        },
    },
    "infrastructure": {
        "allowed_internal": {"domain", "infrastructure"},
        "forbidden_internal": {"application", "web"},
        # Infrastructure can import external libraries
        "forbidden_external": set(),
    },
    "web": {
        "allowed_internal": {"domain", "application", "web"},
        "forbidden_internal": {"infrastructure"},
        "forbidden_external": {"sqlalchemy", "asyncpg", "redis"},
    },
}

# Modern Python code quality checks
MODERN_PYTHON_RULES = {
    "prefer_match_case": {
        "forbidden_patterns": [
            r"if.*isinstance\(.*,.*\):",
            # Long if/elif chains that could use match/case
            r"if.*==.*elif.*==",
        ],
        "mano": "Consider using match/case instead of if/elif with isinstance",
    },
    "use_str_enums": {
        "forbidden_patterns": [
            r"class.*Enum\):",  # Old-style Enum instead of StrEnum
        ],
        "mano": "Consider using StrEnum instead of Enum for string values",
    },
    "avoid_any_types": {
        "forbidden_patterns": [
            r":\s*Any(?![a-zA-Z])",  # Type annotation with Any
            r"dict\[str,\s*Any\]",  # dict[str, Any] patterns
        ],
        "mano": "Avoid using Any types, be more specific where possible",
    },
}

# Domain-specific rules for Mano
MANO_DOMAIN_RULES = {
    # Domain services should not import repository implementations
    "domain/services": {
        "forbidden_patterns": [
            r"from.*infrastructure.*import",
            r"import.*infrastructure",
        ]
    },
    # Repository interfaces should be abstract (ABC) with no implementations
    "domain/repositories": {
        "forbidden_patterns": [
            # Concrete repositories without ABC
            r"class.*Repository\(\s*\):",
            # Concrete method implementations (not docstring/comment)
            r"def .*\([^)]*\):\s*\n\s*[^\"#]",
        ],
        "required_patterns": [
            r"from abc import.*ABC",
            r"@abstractmethod",
        ],
    },
    # Use cases should not directly import infrastructure
    "application/use_cases": {
        "forbidden_patterns": [
            r"from.*infrastructure.*import",
            r"import.*SQLAlchemy",
        ]
    },
    # Value objects should be immutable
    "domain/value_objects": {
        "forbidden_patterns": [
            r"def __setattr__",  # Should not allow attribute setting
            r"self\.\w+\s*=",  # Should not have mutable attributes
        ],
        "required_patterns": [
            r"@dataclass\(frozen=True\)",  # Should be frozen dataclasses
        ],
    },
    # Entities should have proper UUID handling
    "domain/entities": {
        "forbidden_patterns": [
            r"id:\s*int",  # Should use UUID, not int IDs
            r"id\s*=\s*\d+",  # Should not assign integer IDs
        ],
        "required_patterns": [
            r"from.*uuid.*import",  # Should import UUID
        ],
    },
}


class ArchitectureBoundaryChecker:
    """Checks hexagonal architecture boundaries."""

    def __init__(self, enable_modern_checks: bool = True) -> None:
        self.violations: list[tuple[str, int, str]] = []
        self.warnings: list[tuple[str, int, str]] = []
        self.manos: list[tuple[str, int, str]] = []
        self.enable_modern_checks = enable_modern_checks

    def check_file(self, file_path: Path) -> bool:
        """Check a single file for architecture boundary violations."""
        try:
            # Determine the layer from the file path
            layer = self._get_layer_from_path(file_path)
            if not layer:
                return True  # Skip files not in known layers

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse the AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.violations.append((str(file_path), e.lineno or 0, f"Syntax error: {e}"))
                return False

            # Check imports
            self._check_imports(file_path, tree, layer)

            # Check domain-specific rules
            self._check_domain_rules(file_path, content)

            # Check modern Python patterns if enabled
            if self.enable_modern_checks:
                self._check_modern_python_rules(file_path, content)
                self._check_complexity_metrics(file_path, tree)

        except Exception as e:
            self.violations.append((str(file_path), 0, f"Error checking file: {e}"))
            return False
        else:
            return True

    def _get_layer_from_path(self, file_path: Path) -> str:
        """Determine the hexagonal architecture layer from file path."""
        # Special handling for test fixture files - they are allowed to import infrastructure
        # as they serve as the abstraction boundary between tests and infrastructure
        if file_path.name in ("test_fixtures.py", "conftest.py"):
            return ""  # Skip architecture checks for these files

        parts = file_path.parts

        for _i, part in enumerate(parts):
            if part in ["domain", "application", "infrastructure", "web"]:
                return part

        # Check for common patterns in Mano
        path_str = str(file_path).lower()
        if "main.py" in path_str or "api" in path_str or "routers" in path_str:
            return "web"
        if "repositories" in path_str or "database" in path_str:
            return "infrastructure"
        if "use_cases" in path_str or "services" in path_str:
            return "application"
        if "entities" in path_str or "value_objects" in path_str:
            return "domain"

        return ""

    def _check_imports(self, file_path: Path, tree: ast.AST, layer: str) -> None:
        """Check import statements for layer boundary violations."""
        if layer not in LAYER_RULES:
            return

        rules = LAYER_RULES[layer]

        # Find TYPE_CHECKING blocks first
        type_checking_nodes = self._find_type_checking_nodes(tree)

        for node in ast.walk(tree):
            match node:
                case ast.Import() | ast.ImportFrom():
                    # Skip imports inside TYPE_CHECKING blocks
                    if not self._is_node_in_type_checking(node, type_checking_nodes):
                        self._validate_import(file_path, node, layer, rules)

    def _validate_import(self, file_path: Path, node: ast.AST, layer: str, rules: dict[str, Any]) -> None:
        """Validate a single import against layer rules."""
        module_name = self._get_module_name_from_node(node)
        if not module_name:
            return

        self._check_internal_layer_imports(file_path, node, layer, rules, module_name)
        self._check_external_library_imports(file_path, node, layer, rules, module_name)
        self._check_layer_specific_patterns(file_path, node, layer, module_name)

    def _get_module_name_from_node(self, node: ast.AST) -> str:
        """Extract module name from import node."""
        match node:
            case ast.ImportFrom():
                return node.module or ""
            case ast.Import() if node.names:
                return node.names[0].name
            case _:
                return ""

    def _check_internal_layer_imports(
        self, file_path: Path, node: ast.AST, layer: str, rules: dict[str, Any], module_name: str
    ) -> None:
        """Check internal layer imports within the project."""
        if not (module_name.startswith("mano.") or module_name.startswith("...")):
            return

        for forbidden_layer in rules.get("forbidden_internal", set()):
            if forbidden_layer in module_name and not self._is_allowed_exception(
                file_path, layer, forbidden_layer, module_name
            ):
                self.violations.append(
                    (
                        str(file_path),
                        getattr(node, "lineno", 0),
                        (f"Layer '{layer}' cannot import from '{forbidden_layer}' layer: {module_name}"),
                    )
                )

    def _is_allowed_exception(self, file_path: Path, layer: str, forbidden_layer: str, module_name: str) -> bool:
        """Check if this is an allowed exception to the layer rules."""
        # Allow services.py (dependency injection composition root) to import infrastructure
        if file_path.name == "services.py" and layer == "application" and forbidden_layer == "infrastructure":
            return True

        # Allow infrastructure to import from application.ports
        if (
            layer == "infrastructure"
            and forbidden_layer == "application"
            and ("application.ports" in module_name or "application.dtos" in module_name)
        ):
            return True

        # Allow web layer to import from application use cases
        return layer == "web" and forbidden_layer == "application" and "use_cases" in module_name

    def _check_external_library_imports(
        self, file_path: Path, node: ast.AST, layer: str, rules: dict[str, Any], module_name: str
    ) -> None:
        """Check external library imports."""
        for forbidden_lib in rules.get("forbidden_external", set()):
            if module_name.startswith(forbidden_lib):
                self.violations.append(
                    (
                        str(file_path),
                        getattr(node, "lineno", 0),
                        (f"Layer '{layer}' should not directly import '{forbidden_lib}'"),
                    )
                )

    def _check_layer_specific_patterns(self, file_path: Path, node: ast.AST, layer: str, module_name: str) -> None:
        """Check layer-specific import patterns."""
        if layer == "domain":
            self._check_domain_layer_imports(file_path, node, module_name)
        elif layer == "application":
            self._check_application_layer_imports(file_path, node, module_name)

    def _check_domain_layer_imports(self, file_path: Path, node: ast.AST, module_name: str) -> None:
        """Check domain layer specific import restrictions."""
        infrastructure_libs = [
            "sqlalchemy",
            "asyncpg",
            "redis",
            "fastapi",
            "uvicorn",
            "httpx",
            "pydantic",
            "jose",
            "structlog",
        ]
        for lib in infrastructure_libs:
            if module_name.startswith(lib):
                self.violations.append(
                    (
                        str(file_path),
                        getattr(node, "lineno", 0),
                        (f"Domain layer must not depend on infrastructure library: {module_name}"),
                    )
                )

    def _check_application_layer_imports(self, file_path: Path, node: ast.AST, module_name: str) -> None:
        """Check application layer specific import restrictions."""
        forbidden_implementations = ["SQLAlchemy", "AsyncSession", "redis.Redis"]
        if any(impl in module_name for impl in forbidden_implementations):
            self.violations.append(
                (
                    str(file_path),
                    getattr(node, "lineno", 0),
                    (f"Application layer should not import concrete infrastructure implementations: {module_name}"),
                )
            )

    def _find_type_checking_nodes(self, tree: ast.AST) -> list[ast.If]:
        """Find all TYPE_CHECKING if statements in the AST."""
        type_checking_nodes = []

        for node in ast.walk(tree):
            match node:
                case ast.If():
                    # Check if this is a TYPE_CHECKING if statement
                    if self._is_type_checking_if(node):
                        type_checking_nodes.append(node)
                case _:
                    pass

        return type_checking_nodes

    def _is_type_checking_if(self, node: ast.If) -> bool:
        """Check if an If node is a TYPE_CHECKING block."""
        match node.test:
            case ast.Name(id="TYPE_CHECKING"):
                # Check for: if TYPE_CHECKING:
                return True
            case ast.Attribute(attr="TYPE_CHECKING", value=ast.Name(id="typing")):
                # Check for: if typing.TYPE_CHECKING:
                return True
            case _:
                return False

    def _is_node_in_type_checking(self, node: ast.AST, type_checking_nodes: list[ast.If]) -> bool:
        """Check if a node is inside any TYPE_CHECKING block."""
        return any(self._is_node_descendant(node, type_checking_node) for type_checking_node in type_checking_nodes)

    def _is_node_descendant(self, node: ast.AST, ancestor: ast.AST) -> bool:
        """Check if a node is a descendant of an ancestor node."""
        return any(child is node for child in ast.walk(ancestor))

    def _check_domain_rules(self, file_path: Path, content: str) -> None:
        """Check domain-specific architectural rules."""
        path_str = str(file_path)

        for pattern, rules in MANO_DOMAIN_RULES.items():
            if pattern in path_str:
                lines = content.split("\n")

                # Check forbidden patterns
                for forbidden_pattern in rules.get("forbidden_patterns", []):
                    for line_num, line in enumerate(lines, 1):
                        if re.search(forbidden_pattern, line):
                            self.violations.append(
                                (
                                    str(file_path),
                                    line_num,
                                    (f"Forbidden pattern in {pattern}: {forbidden_pattern}"),
                                )
                            )

                # Check required patterns (for repository interfaces,
                # but not __init__.py)
                if "repositories" in pattern and rules.get("required_patterns") and file_path.name != "__init__.py":
                    for required_pattern in rules["required_patterns"]:
                        if not re.search(required_pattern, content):
                            self.warnings.append(
                                (
                                    str(file_path),
                                    0,
                                    (f"Repository interface should include: {required_pattern}"),
                                )
                            )

    def _check_modern_python_rules(self, file_path: Path, content: str) -> None:
        """Check modern Python coding patterns and best practices."""
        lines = content.split("\n")

        for _rule_name, rule_config in MODERN_PYTHON_RULES.items():
            for forbidden_pattern in rule_config["forbidden_patterns"]:
                for line_num, line in enumerate(lines, 1):
                    if re.search(forbidden_pattern, line, re.IGNORECASE):
                        # Skip comments and docstrings
                        stripped_line = line.strip()
                        if stripped_line.startswith("#") or '"""' in stripped_line or "'''" in stripped_line:
                            continue

                        self.manos.append(
                            (
                                str(file_path),
                                line_num,
                                f"{rule_config['mano']}: {line.strip()}",
                            )
                        )

    def _check_complexity_metrics(self, file_path: Path, tree: ast.AST) -> None:
        """Check code complexity metrics."""

        # Count nested functions/classes
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.nesting_level = 0
                self.max_nesting = 0
                self.function_lengths = []

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)

                # Calculate function length
                if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                    func_length = node.end_lineno - node.lineno + 1
                    self.function_lengths.append((node.name, func_length, node.lineno))

                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self.visit_FunctionDef(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)

        # Report excessive nesting
        if visitor.max_nesting > MAX_NESTING_LEVEL:
            self.warnings.append(
                (
                    str(file_path),
                    0,
                    (f"High nesting level detected ({visitor.max_nesting}). Consider refactoring."),
                )
            )

        # Report long functions
        for func_name, length, line_num in visitor.function_lengths:
            if length > MAX_FUNCTION_LENGTH:
                self.warnings.append(
                    (
                        str(file_path),
                        line_num,
                        (f"Function '{func_name}' is {length} lines long. Consider breaking it down."),
                    )
                )

    def get_results(
        self,
    ) -> tuple[
        list[tuple[str, int, str]],
        list[tuple[str, int, str]],
        list[tuple[str, int, str]],
    ]:
        """Get checking results."""
        return self.violations, self.warnings, self.manos


def _create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="Check hexagonal architecture boundaries and code quality for Mano")
    parser.add_argument("files", nargs="*", help="Files to check")
    parser.add_argument(
        "--no-modern-checks",
        action="store_true",
        help="Disable modern Python pattern checks",
    )
    parser.add_argument(
        "--manos-only",
        action="store_true",
        help="Only show manos, not violations or warnings",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed information about checks",
    )
    return parser


def _get_files_to_check(args: argparse.Namespace) -> list[Path]:
    """Get the list of files to check based on arguments."""
    if args.files:
        return [Path(f) for f in args.files if Path(f).exists()]

    # Check all Python files in src/
    src_dir = Path("src")
    return list(src_dir.rglob("*.py")) if src_dir.exists() else []


def _print_violations(violations: list) -> int:
    """Print violations and return exit code."""
    if not violations:
        return 0

    print("Architecture boundary violations found:")
    for file_path_str, line_num, message in violations:
        location = f"{file_path_str}:{line_num}" if line_num > 0 else file_path_str
        print(f"  {location}: {message}")

    return 1


def _print_warnings(warnings: list) -> None:
    """Print warnings."""
    if not warnings:
        return

    print("\n⚠️  Architecture boundary warnings:")
    for file_path_str, line_num, message in warnings:
        location = f"{file_path_str}:{line_num}" if line_num > 0 else file_path_str
        print(f"  {location}: {message}")


def _print_manos(manos: list) -> None:
    """Print manos."""
    if not manos:
        return

    print("\n💡 Code modernization manos:")
    for file_path_str, line_num, message in manos:
        location = f"{file_path_str}:{line_num}" if line_num > 0 else file_path_str
        print(f"  {location}: {message}")


def _print_results(violations: list, warnings: list, manos: list, args: argparse.Namespace) -> int:
    """Print the checking results and return appropriate exit code."""
    exit_code = 0

    if not args.manos_only:
        exit_code = _print_violations(violations)
        _print_warnings(warnings)

    if manos and not args.no_modern_checks:
        _print_manos(manos)

    return exit_code


def _print_summary(violations: list, warnings: list, manos: list, files_checked: int, args: argparse.Namespace) -> None:
    """Print summary information."""
    if not violations and not warnings and not manos:
        print(f"✅ All checks passed for {files_checked} files")
        return

    if args.verbose:
        print("\n📊 Summary:")
        print(f"  Files checked: {files_checked}")
        print(f"  Violations: {len(violations)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  manos: {len(manos)}")

    if violations and not args.manos_only:
        print("\n🏗️ Hexagonal architecture principles:")
        print("  - Domain: No external dependencies, only business logic")
        print("  - Application: Orchestrates domain, no infrastructure imports")
        print("  - Infrastructure: Implements technical details, adapters")
        print("  - Web: Handles external interfaces, no direct infrastructure")


def main() -> int:
    """Main function to check architecture boundaries."""
    parser = _create_argument_parser()
    args = parser.parse_args()

    checker = ArchitectureBoundaryChecker(enable_modern_checks=not args.no_modern_checks)
    files_to_check = _get_files_to_check(args)

    if args.verbose:
        print(f"🔍 Checking {len(files_to_check)} Python files...")

    files_checked = sum(1 for file_path in files_to_check if checker.check_file(file_path))
    violations, warnings, manos = checker.get_results()

    exit_code = _print_results(violations, warnings, manos, args)
    _print_summary(violations, warnings, manos, files_checked, args)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
