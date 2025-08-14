import logging

from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

import exasol.slc_ci.lib.get_build_runner as lib_get_build_runner
from exasol.slc_ci.cli.cli import cli
from exasol.slc_ci.cli.options.flavor_options import flavor_options
from exasol.slc_ci.cli.options.github_options import github_options
from exasol.slc_ci.lib.github_access import GithubAccess


@cli.command()
@add_options(flavor_options)
@add_options(github_options)
def get_build_runner(flavor: str, github_output_var: str):
    logging.basicConfig(level=logging.INFO)
    github_access = GithubAccess(github_output_var)
    lib_get_build_runner.get_build_runner(flavor=flavor, github_access=github_access)
