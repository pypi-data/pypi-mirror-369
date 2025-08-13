"""Test db lookup."""

import mammos_entity as me
import pytest

from mammos_dft.db import get_micromagnetic_properties


def test_Co2Fe2H4():
    """Test material `Co2Fe2H4`.

    There is only one material with formula `Co2Fe2H4`, so this
    test should load its table without issues.
    """
    properties = get_micromagnetic_properties(
        chemical_formula="Co2Fe2H4", print_info=False
    )
    Ms_true = me.Ms(1190240.2412648, unit="A/m")
    Ku_true = me.Ku(2810000, unit="J/m3")
    assert Ms_true == properties.Ms_0
    assert Ku_true == properties.Ku_0


def test_Nd2Fe14B():
    """Test material `Nd2Fe14B`.

    There is only one material with such formula in the database,
    so we test it with the values we know to be true.
    """
    properties = get_micromagnetic_properties(
        chemical_formula="Nd2Fe14B", print_info=False
    )
    Ms_true = me.Ms(1280000, unit="A/m")
    Ku_true = me.Ku(4300000, unit="J/m3")
    assert Ms_true == properties.Ms_0
    assert Ku_true == properties.Ku_0


def test_CrNiP():
    """Test material `CrNiP`.

    There is no material with such formula in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_micromagnetic_properties(chemical_formula="CrNiP")


def test_Co2Fe2H4_12():
    """Test material `Co2Fe2H4` with space group number `12`.

    There is no material with such formula and space group
    in the database, so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_micromagnetic_properties(chemical_formula="Co2Fe2H4", space_group_number=12)


def test_all():
    """Test search with no filters.

    This will select all entries in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_micromagnetic_properties(print_info=False)
