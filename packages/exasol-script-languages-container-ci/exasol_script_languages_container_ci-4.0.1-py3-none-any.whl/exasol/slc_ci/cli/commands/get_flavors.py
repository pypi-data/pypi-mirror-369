import logging

from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

import exasol.slc_ci.lib.get_flavors as lib_get_flavors
from exasol.slc_ci.cli.cli import cli
from exasol.slc_ci.cli.options.github_options import github_options
from exasol.slc_ci.lib.github_access import GithubAccess


@cli.command()
@add_options(github_options)
def get_flavors(
    github_output_var: str,
):
    """
    Searches for all available flavors and writes result as JSON array to Github variable <github-output-var>.
    """
    logging.basicConfig(level=logging.INFO)
    github_access: GithubAccess = GithubAccess(github_output_var=github_output_var)
    lib_get_flavors.get_flavors(github_access=github_access)
