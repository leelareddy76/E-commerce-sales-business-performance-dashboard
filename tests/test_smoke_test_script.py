import importlib.util
from pathlib import Path


def test_smoke_test_module_import_has_no_side_effects():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "smoke_test.py"
    spec = importlib.util.spec_from_file_location("smoke_test_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "main")
