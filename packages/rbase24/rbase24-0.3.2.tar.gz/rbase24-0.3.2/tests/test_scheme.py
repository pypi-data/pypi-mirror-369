from pathlib import Path

import pytest
from rbase24.config import Base24ViewerConfig
from rbase24.scheme import list_schemes, load_scheme


@pytest.mark.unit
def test_scheme_load_base16_scheme():
    cf = Path(__file__).parent / "config.ini"
    cfg = Base24ViewerConfig(cf)
    scheme_dir = cfg.scheme_dir
    assert scheme_dir is not None
    scheme_dir = Path(__file__).parent / scheme_dir
    scheme = load_scheme(scheme_dir / "base16" / "horizon-light.yaml")
    assert "fdf0ed" == scheme["palette"]["base00"]


@pytest.mark.unit
def test_scheme_load_base24_scheme():
    cf = Path(__file__).parent / "config.ini"
    cfg = Base24ViewerConfig(cf)
    scheme_dir = cfg.scheme_dir
    assert scheme_dir is not None
    scheme_dir = Path(__file__).parent / scheme_dir
    scheme = load_scheme(scheme_dir / "base24" / "brogrammer.yaml")
    assert "524fb9" == scheme["palette"].get("base17", None)


@pytest.mark.unit
def test_scheme_list_schemes():
    cf = Path(__file__).parent / "config.ini"
    cfg = Base24ViewerConfig(cf)
    scheme_dir = cfg.scheme_dir
    assert scheme_dir is not None
    scheme_dir = Path(__file__).parent / scheme_dir

    assert 10 == len(list_schemes(scheme_dir))
