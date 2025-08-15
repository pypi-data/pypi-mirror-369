"""
Dummy tests
"""

import numpy as np
import pytest

from example_fgen_basic.get_wavelength import get_wavelength, get_wavelength_plain


def test_plain():
    np.testing.assert_allclose(get_wavelength_plain(400.0e12), 749.48e-9)


def test_units():
    pint = pytest.importorskip("pint")
    pint_testing = pytest.importorskip("pint.testing")

    ur = pint.get_application_registry()

    pint_testing.assert_allclose(
        get_wavelength(ur.Quantity(400.0, "THz")).to("nm"),
        ur.Quantity(749.48, "nm"),
    )
