"""
Inject source files into `meson.build`

Easier than doing this by hand and allows us to include this in pre-commit
"""

from __future__ import annotations

import re
import textwrap
from collections.abc import Iterable
from pathlib import Path


def get_src_pattern(meson_variable: str) -> str:
    """
    Get the pattern to use to find the source files in `meson.build`

    Parameters
    ----------
    meson_variable
        Meson variable to set

    Returns
    -------
    :
        Pattern to use to grep for the meson variable
    """
    return rf"{meson_variable} = files\(\s*('[a-z\/_\.0-9]*',\s*)*\)"


def get_src_substitution(
    meson_variable: str, srcs: Iterable[Path], rel_to: Path
) -> str:
    """
    Get the value to substitute for the meson variable

    Parameters
    ----------
    meson_variable
        Meson variable to set

    srcs
        Sources to use for this meson variable

    rel_to
        Path the sources should be relative to when setting `meson_variable`

    Returns
    -------
    :
        Value to use to set the meson variable
    """
    inner = textwrap.indent(
        ",\n".join(f"'{v.relative_to(rel_to).as_posix()}'" for v in srcs),
        prefix=" " * 4,
    )

    res = f"{meson_variable} = files(\n{inner},\n  )"
    return res


def main():
    """
    Inject sources into `meson.build`

    Nicer than typing by hand
    """
    REPO_ROOT = Path(__file__).parents[1]
    SRC_DIR = REPO_ROOT / "src"

    srcs = []
    srcs_ancillary_lib = []
    for ffile in SRC_DIR.rglob("*.f90"):
        if ffile.name.endswith("_wrapper.f90"):
            srcs.append(ffile)
        else:
            srcs_ancillary_lib.append(ffile)

    python_srcs = tuple(SRC_DIR.rglob("*.py"))

    with open(REPO_ROOT / "meson.build") as fh:
        meson_build_in = fh.read().strip()

    meson_build_out = meson_build_in
    for meson_variable, src_paths in (
        ("srcs", srcs),
        ("srcs_ancillary_lib", srcs_ancillary_lib),
        ("python_srcs", python_srcs),
    ):
        pattern = get_src_pattern(meson_variable)
        substitution = get_src_substitution(
            meson_variable, sorted(src_paths), REPO_ROOT
        )

        meson_build_out = re.sub(pattern, substitution, meson_build_out)

    with open(REPO_ROOT / "meson.build", "w") as fh:
        fh.write(meson_build_out)
        fh.write("\n")


if __name__ == "__main__":
    main()
