#!/usr/bin/env python3
"""
This script updates the version across multiple files:
 - docsible/cli.py (the function get_version() returns the version)
 - setup.py (e.g., version='0.7.10')
 - pyproject.toml (e.g., version = "0.7.10")

It supports two actions:
  - "bump": increments the patch version (e.g. 0.7.10 -> 0.7.11)
  - "revert": decrements the patch version (e.g. 0.7.10 -> 0.7.9)
  
Usage:
    python scripts/change_version.py bump
    python scripts/change_version.py revert
"""

import os
import re
import sys
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def change_version(version_str: str, bump: bool = True) -> str:
    """
    Change the patch version number.

    Args:
        version_str (str): A semantic version string in the format 'major.minor.patch'
        bump (bool): If True, increment the patch version; if False, decrement it.

    Returns:
        str: The updated version string.

    Raises:
        ValueError: If the version format is invalid.
    """
    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)$"
    match = re.match(semver_pattern, version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    major, minor, patch = map(int, match.groups())
    if bump:
        patch += 1
    else:
        if patch == 0:
            logging.error("Cannot revert version: patch version is already 0.")
            sys.exit(1)
        patch -= 1
    return f"{major}.{minor}.{patch}"


def update_file(file_path: str, pattern: str, replacement_format: str, new_version: str):
    """
    Updates a file by replacing the version string with the new version.

    Args:
        file_path (str): The path to the file.
        pattern (str): A regex pattern to find the version string.
        replacement_format (str): A format string using explicit group references.
        new_version (str): The new version string to inject.
    """
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} does not exist.")
        sys.exit(1)
    with open(file_path, "r") as f:
        content = f.read()
    if not re.search(pattern, content):
        logging.error(f"Version string not found in {file_path}")
        sys.exit(1)
    new_content = re.sub(
        pattern, replacement_format.format(new_version), content)
    with open(file_path, "w") as f:
        f.write(new_content)
    logging.info(f"Updated {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bump or revert version across multiple files."
    )
    parser.add_argument(
        "action",
        choices=["bump", "revert"],
        help="Action to perform: 'bump' to increment or 'revert' to decrement the patch version.",
    )
    args = parser.parse_args()

    # Files to update.
    cli_file = os.path.join("docsible", "cli.py")
    setup_file = "setup.py"
    pyproject_file = "pyproject.toml"

    # Define regex patterns and replacement strings using explicit group references.
    cli_pattern = r'(def\s+get_version\(\):\s+return\s+["\'])(\d+\.\d+\.\d+)(["\'])'
    cli_replacement = r'\g<1>{}\g<3>'
    setup_pattern = r'(version\s*=\s*["\'])(\d+\.\d+\.\d+)(["\'])'
    setup_replacement = r'\g<1>{}\g<3>'
    pyproject_pattern = r'(version\s*=\s*["\'])(\d+\.\d+\.\d+)(["\'])'
    pyproject_replacement = r'\g<1>{}\g<3>'

    # Read the current version from cli.py.
    try:
        with open(cli_file, "r") as f:
            cli_content = f.read()
    except Exception as e:
        logging.error(f"Error reading {cli_file}: {e}")
        sys.exit(1)

    cli_match = re.search(cli_pattern, cli_content)
    if not cli_match:
        logging.error("Could not find version string in docsible/cli.py")
        sys.exit(1)
    current_version = cli_match.group(2)
    logging.info(f"Current version in cli.py: {current_version}")

    # Decide the new version based on the requested action.
    if args.action == "bump":
        new_version = change_version(current_version, bump=True)
        logging.info(f"Bumping version to: {new_version}")
    else:
        new_version = change_version(current_version, bump=False)
        logging.info(f"Reverting version to: {new_version}")

    # Update all files with the new version.
    update_file(cli_file, cli_pattern, cli_replacement, new_version)
    update_file(setup_file, setup_pattern, setup_replacement, new_version)
    update_file(pyproject_file, pyproject_pattern,
                pyproject_replacement, new_version)

    logging.info(f"Version update complete. New version: {new_version}")


if __name__ == "__main__":
    main()
