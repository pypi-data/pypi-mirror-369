"""
Propogate information from `pyproject.toml` to other parts of the project as needed
"""

from __future__ import annotations

import re
from pathlib import Path

import tomllib


def main():
    """
    Propogate information from `pyproject.toml` to the rest of the project files
    """
    REPO_ROOT = Path(__file__).parents[1]
    with open(REPO_ROOT / "pyproject.toml", "rb") as fh:
        pyproject_toml = tomllib.load(fh)

    project_name = pyproject_toml["project"]["name"]
    project_name_python = project_name.replace("-", "_")
    version = pyproject_toml["project"]["version"]
    if re.match(".*[a-z].*", version):
        # Can't use pre-releases in meson.build, switch to dev version
        version = "0.0.0"

    description = pyproject_toml["project"]["description"]

    with open(REPO_ROOT / "meson.build") as fh:
        meson_build_in = fh.read().strip()

    meson_build_out = meson_build_in
    for pattern, substitution in (
        (r"version\: '[0-9a-z\.]*'", f"version: '{version}'"),
        (
            r"python_project_name = '[a-z\-_]*'",
            f"python_project_name = '{project_name_python}'",
        ),
        (r"project\(\s*'[a-z\-_]*'", f"project(\n  '{project_name}'"),
        (
            "description: '.*'",
            f"description: '{description}. This is the standalone Fortran library.'",
        ),
    ):
        meson_build_out = re.sub(pattern, substitution, meson_build_out)

    with open(REPO_ROOT / "meson.build", "w") as fh:
        fh.write(meson_build_out)
        fh.write("\n")


if __name__ == "__main__":
    main()
