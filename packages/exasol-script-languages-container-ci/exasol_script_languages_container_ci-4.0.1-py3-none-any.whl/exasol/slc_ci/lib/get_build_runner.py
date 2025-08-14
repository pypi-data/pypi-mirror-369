from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.get_flavor_ci_model import get_flavor_ci_model
from exasol.slc_ci.lib.github_access import GithubAccess


def get_build_runner(flavor: str, github_access: GithubAccess):
    build_config = get_build_config_model()
    flavor_config = get_flavor_ci_model(build_config, flavor)
    github_access.write_result(flavor_config.build_runner)
