import logging

import click
from exasol_integration_test_docker_environment.lib.utils.cli_function_decorators import (
    add_options,
)

import exasol.slc_ci.lib.export_and_scan_vulnerabilities as lib_export_and_scan_vulnerabilities
from exasol.slc_ci.cli.cli import cli
from exasol.slc_ci.cli.options.branch_options import branch_option, commit_sha_option
from exasol.slc_ci.cli.options.docker_options import docker_options
from exasol.slc_ci.cli.options.flavor_options import flavor_options
from exasol.slc_ci.cli.options.github_options import github_options
from exasol.slc_ci.lib.ci_build import CIBuild
from exasol.slc_ci.lib.ci_export import CIExport
from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_push import CIPush
from exasol.slc_ci.lib.ci_security_scan import CISecurityScan
from exasol.slc_ci.lib.git_access import GitAccess
from exasol.slc_ci.lib.github_access import GithubAccess
from exasol.slc_ci.model.build_mode import BuildMode, buildModeValues, defaultBuildMode


@cli.command()
@add_options(flavor_options)
@add_options([branch_option, commit_sha_option])
@add_options(docker_options)
@add_options(
    [
        click.option(
            "--build-mode",
            type=click.Choice(buildModeValues()),
            required=True,
            help=f"""Build mode. Possible values: {buildModeValues()}""",
        )
    ]
)
@add_options(github_options)
def export_and_scan_vulnerabilities(
    flavor: str,
    branch_name: str,
    docker_user: str,
    docker_password: str,
    commit_sha: str,
    build_mode: str,
    github_output_var: str,
) -> None:
    logging.basicConfig(level=logging.INFO)
    git_access: GitAccess = GitAccess()
    github_access: GithubAccess = GithubAccess(github_output_var)
    ci_build = CIBuild()
    ci_security_scan = CISecurityScan()
    ci_prepare = CIPrepare()
    ci_export = CIExport()
    ci_push = CIPush()

    lib_export_and_scan_vulnerabilities.export_and_scan_vulnerabilities(
        build_mode=BuildMode[build_mode.upper()],
        flavor=flavor,
        branch_name=branch_name,
        docker_user=docker_user,
        docker_password=docker_password,
        commit_sha=commit_sha,
        git_access=git_access,
        github_access=github_access,
        ci_build=ci_build,
        ci_security_scan=ci_security_scan,
        ci_prepare=ci_prepare,
        ci_export=ci_export,
        ci_push=ci_push,
    )
