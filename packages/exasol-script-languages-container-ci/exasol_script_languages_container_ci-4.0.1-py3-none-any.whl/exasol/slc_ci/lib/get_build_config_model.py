from pathlib import Path

from exasol.slc_ci.model.build_config_model import BuildConfig


def _find_build_config_path() -> Path:
    """
    Traverse paths upwards until starting from cwd until finding "build_config.json".
    If not found, raises FileNotFoundError.
    """
    base_path = Path.cwd()
    for test_paths in [base_path] + list(base_path.parents):
        current_build_config_path = test_paths / "build_config.json"
        if current_build_config_path.exists():
            return current_build_config_path
    raise FileNotFoundError("Could not find build config file")


def get_build_config_model() -> BuildConfig:
    build_config_path = _find_build_config_path()
    return BuildConfig.model_validate_json(build_config_path.read_text(), strict=True)
