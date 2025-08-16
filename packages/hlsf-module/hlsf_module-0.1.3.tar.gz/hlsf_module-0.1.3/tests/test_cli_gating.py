import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from hlsf_module.cli import parse_args


def test_parse_gating_options():
    args = parse_args([
        "--res-threshold",
        "0.3",
        "--gate-duration",
        "4",
        "--gate-margin",
        "0.2",
        "--gate-detectors",
        "2",
        "--gate-strategy",
        "ema",
        "--gate-ema-alpha",
        "0.7",
        "--cross-weight",
        "0.1",
    ])
    assert args.gate_margin == 0.2
    assert args.gate_detectors == 2
    assert args.gate_strategy == "ema"
    assert args.gate_ema_alpha == 0.7
    assert args.cross_weight == 0.1
