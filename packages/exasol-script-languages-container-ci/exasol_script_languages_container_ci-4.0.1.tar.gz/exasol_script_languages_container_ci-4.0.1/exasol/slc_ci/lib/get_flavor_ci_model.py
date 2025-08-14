from exasol.slc_ci.model.build_config_model import BuildConfig
from exasol.slc_ci.model.flavor_ci_model import FlavorCiConfig


def get_flavor_ci_model(build_config: BuildConfig, flavor: str) -> FlavorCiConfig:
    flavor_ci_config_path = build_config.flavors_path / flavor / "ci.json"
    return FlavorCiConfig.model_validate_json(
        flavor_ci_config_path.read_text(), strict=True
    )
