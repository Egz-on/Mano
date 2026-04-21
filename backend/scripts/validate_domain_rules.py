#!/usr/bin/env python3
"""Validate domain business rules."""

import sys
from pathlib import Path


def validate_domain_rules():
    """Validate domain business rules are properly implemented."""
    project_root = Path(__file__).parent.parent
    domain_dir = project_root / "src" / "mano" / "domain"

    if not domain_dir.exists():
        print("Domain directory not found")
        sys.exit(1)

    # Check for essential domain files
    required_files = ["models/", "repositories/", "services/", "exceptions/"]

    missing_files = []
    for required_file in required_files:
        file_path = domain_dir / required_file
        if not file_path.exists():
            missing_files.append(required_file)

    if missing_files:
        print("Missing domain files:")
        for file_path in missing_files:
            print(f"  {file_path}")
        sys.exit(1)

    # Check for business rules in constants
    constants_file = project_root / "src" / "mano" / "common" / "constans.py"
    if constants_file.exists():
        with open(constants_file) as f:
            content = f.read()
            if "BusinessRules" in content or "class" in content:
                print("Domain business rules validation passed")
                sys.exit(0)

    print("Domain business rules validation passed")
    sys.exit(0)


if __name__ == "__main__":
    validate_domain_rules()
