import pytest

from hlsf_module.cli import parse_args


def test_options_registered_once(capsys):
    """--pre-mode and --edge-file should appear once in help output."""
    with pytest.raises(SystemExit):
        parse_args(["--help"])
    help_text = capsys.readouterr().out
    pre_lines = [l for l in help_text.splitlines() if l.lstrip().startswith("--pre-mode")]
    edge_lines = [l for l in help_text.splitlines() if l.lstrip().startswith("--edge-file")]
    assert len(pre_lines) == 1
    assert len(edge_lines) == 1


def test_invalid_preemphasis_raises(capsys):
    with pytest.raises(SystemExit):
        parse_args(["--preemphasis", "1.5"])
    assert "pre-emphasis alpha must be in [0, 1)" in capsys.readouterr().err


def test_invalid_edge_file(tmp_path, capsys):
    edge = tmp_path / "edges.txt"
    edge.write_text("0 2 1")
    with pytest.raises(SystemExit):
        parse_args(["--edge-file", str(edge)])
    err = capsys.readouterr().err
    assert "edge frequencies must be strictly increasing" in err
