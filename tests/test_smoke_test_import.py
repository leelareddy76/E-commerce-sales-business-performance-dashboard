from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_smoke_test_module_import_has_no_side_effect_exit():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "smoke_test.py"
    spec = spec_from_file_location("scripts.smoke_test", script_path)
    module = module_from_spec(spec)

    spec.loader.exec_module(module)

    assert callable(module.main)
