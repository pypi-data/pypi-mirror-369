import mammos_dft


def test_version():
    """Check that __version__ exists and is a string."""
    assert isinstance(mammos_dft.__version__, str)
