import logging

import click
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

import exasol.slc_ci.lib.prepare_test_container as lib_prepare_test_container
from exasol.slc_ci.cli.cli import cli
from exasol.slc_ci.cli.options.branch_options import commit_sha_option
from exasol.slc_ci.cli.options.docker_options import docker_options
from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_push_test_container import CIPushTestContainer


@cli.command()
@add_options([commit_sha_option])
@add_options(docker_options)
def prepare_test_container(
    commit_sha: str,
    docker_user: str,
    docker_password: str,
) -> None:
    logging.basicConfig(level=logging.INFO)
    ci_push_test_container = CIPushTestContainer()
    ci_prepare = CIPrepare()
    lib_prepare_test_container.prepare_test_container(
        commit_sha=commit_sha,
        docker_user=docker_user,
        docker_password=docker_password,
        ci_push_test_container=ci_push_test_container,
        ci_prepare=ci_prepare,
    )
