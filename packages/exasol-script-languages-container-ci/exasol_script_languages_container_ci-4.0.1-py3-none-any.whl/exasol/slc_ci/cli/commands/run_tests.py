import logging

import click
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

import exasol.slc_ci.lib.run_tests as lib_run_tests
from exasol.slc_ci.cli.cli import cli
from exasol.slc_ci.cli.options.branch_options import commit_sha_option
from exasol.slc_ci.cli.options.docker_options import docker_options
from exasol.slc_ci.cli.options.flavor_options import flavor_options
from exasol.slc_ci.cli.options.test_options import test_set_options
from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_test import CIExecuteTest


@cli.command()
@add_options(flavor_options)
@add_options(
    [
        click.option(
            "--slc-directory",
            type=str,
            required=True,
            help="Directory where existing SLC file is stored.",
        ),
    ]
)
@add_options(test_set_options)
@add_options(docker_options)
@add_options([commit_sha_option])
def run_tests(
    flavor: str,
    slc_directory: str,
    test_set_name: str,
    docker_user: str,
    docker_password: str,
    commit_sha: str,
) -> None:
    logging.basicConfig(level=logging.INFO)
    ci_prepare = CIPrepare()
    ci_test = CIExecuteTest()
    lib_run_tests.run_tests(
        flavor=flavor,
        slc_directory=slc_directory,
        test_set_name=test_set_name,
        docker_user=docker_user,
        docker_password=docker_password,
        ci_prepare=ci_prepare,
        ci_test=ci_test,
        commit_sha=commit_sha,
    )
