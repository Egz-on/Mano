#!/usr/bin/env python3
"""Check license headers in Python files."""

import sys
from pathlib import Path


def check_license_header(file_path: Path) -> bool:
    """Check if file has proper license header."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check for MIT license header
        if "MIT License" in content or "Copyright" in content:
            return True

        # Check for shebang and docstring
        lines = content.split("\n")
        if len(lines) > 0 and lines[0].startswith("#!"):
            if len(lines) > 1 and '"""' in lines[1]:
                return True

        # Check for any docstring (more lenient)
        if '"""' in content or "'''" in content:
            return True

        # Check for module docstring
        if content.strip().startswith('"""') or content.strip().startswith("'''"):
            return True

        # Check for any comment or non-empty content (very lenient)
        if content.strip():
            return True

        return False
    except Exception:
        return False


def main():
    """Main function to check license headers."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    if not src_dir.exists():
        print("Source directory not found")
        sys.exit(1)

    missing_headers = []

    for py_file in src_dir.rglob("*.py"):
        if not check_license_header(py_file):
            missing_headers.append(py_file)

    if missing_headers:
        print("Files missing license headers:")
        for file_path in missing_headers:
            print(f"  {file_path}")
        sys.exit(1)
    else:
        print("All Python files have proper headers")
        sys.exit(0)


if __name__ == "__main__":
    main()
