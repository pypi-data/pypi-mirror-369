import json
import logging
from typing import Tuple

from exasol.slc_ci.lib.branch_config import push_to_docker_release_repo
from exasol.slc_ci.lib.ci_build import CIBuild
from exasol.slc_ci.lib.ci_export import CIExport
from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_push import CIPush
from exasol.slc_ci.lib.ci_security_scan import CISecurityScan
from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.git_access import GitAccess
from exasol.slc_ci.lib.github_access import GithubAccess
from exasol.slc_ci.model.build_config_model import BuildConfig
from exasol.slc_ci.model.build_mode import BuildMode


def _export_slc(
    ci_export: CIExport, github_access: GithubAccess, flavor_path: tuple[str, ...]
) -> None:
    release_output = ".build_output_release"
    slc_release = ci_export.export(
        flavor_path=flavor_path, goal="release", output_directory=release_output
    )
    test_output = ".build_output_test"
    slc_test = ci_export.export(
        flavor_path=flavor_path,
        goal="base_test_build_run",
        output_directory=test_output,
    )
    github_access.write_result(
        json.dumps(
            {
                "slc_release": {"path": str(slc_release), "goal": "release"},
                "slc_test": {"path": str(slc_test), "goal": "base_test_build_run"},
            }
        )
    )


def _export_and_scan_vulnerabilities_ci(
    flavor: str,
    branch_name: str,
    docker_user: str,
    docker_password: str,
    commit_sha: str,
    rebuild: bool,
    git_access: GitAccess,
    github_access: GithubAccess,
    ci_build: CIBuild = CIBuild(),
    ci_security_scan: CISecurityScan = CISecurityScan(),
    ci_prepare: CIPrepare = CIPrepare(),
    ci_export: CIExport = CIExport(),
    ci_push: CIPush = CIPush(),
) -> None:
    logging.info(
        f"Running build image and scan vulnerabilities for parameters: {locals()}"
    )
    build_config: BuildConfig = get_build_config_model()

    flavor_path = (f"{build_config.flavors_path}/{flavor}",)
    test_container_folder = build_config.test_container_folder
    ci_prepare.prepare(commit_sha=commit_sha)
    ci_build.build(
        flavor_path=flavor_path,
        rebuild=rebuild,
        build_docker_repository=build_config.docker_build_repository,
        docker_user=docker_user,
        docker_password=docker_password,
    )
    ci_security_scan.run_security_scan(flavor_path=flavor_path)
    ci_push.push(
        flavor_path=flavor_path,
        target_docker_repository=build_config.docker_build_repository,
        target_docker_tag_prefix=commit_sha,
        docker_user=docker_user,
        docker_password=docker_password,
    )
    ci_push.push(
        flavor_path=flavor_path,
        target_docker_repository=build_config.docker_build_repository,
        target_docker_tag_prefix="",
        docker_user=docker_user,
        docker_password=docker_password,
    )
    if push_to_docker_release_repo(branch_name):
        ci_push.push(
            flavor_path=flavor_path,
            target_docker_repository=build_config.docker_release_repository,
            target_docker_tag_prefix="",
            docker_user=docker_user,
            docker_password=docker_password,
        )

    _export_slc(ci_export, github_access, flavor_path)


def _export_and_scan_vulnerabilities_cd(
    flavor: str,
    branch_name: str,
    docker_user: str,
    docker_password: str,
    commit_sha: str,
    git_access: GitAccess,
    github_access: GithubAccess,
    ci_build: CIBuild = CIBuild(),
    ci_security_scan: CISecurityScan = CISecurityScan(),
    ci_prepare: CIPrepare = CIPrepare(),
    ci_export: CIExport = CIExport(),
    ci_push: CIPush = CIPush(),
) -> None:
    logging.info(
        f"Running build image and scanning vulnerabilities for release for parameters: {locals()}"
    )
    build_config: BuildConfig = get_build_config_model()

    flavor_path = (f"{build_config.flavors_path}/{flavor}",)
    test_container_folder = build_config.test_container_folder
    ci_prepare.prepare(commit_sha=commit_sha)
    ci_build.build(
        flavor_path=flavor_path,
        rebuild=True,
        build_docker_repository=build_config.docker_build_repository,
        docker_user=docker_user,
        docker_password=docker_password,
    )
    ci_security_scan.run_security_scan(flavor_path=flavor_path)
    ci_push.push(
        flavor_path=flavor_path,
        target_docker_repository=build_config.docker_release_repository,
        target_docker_tag_prefix="",
        docker_user=docker_user,
        docker_password=docker_password,
    )
    _export_slc(ci_export, github_access, flavor_path)


def export_and_scan_vulnerabilities(
    build_mode: BuildMode = BuildMode.NORMAL, **kwargs
) -> None:
    if build_mode == BuildMode.NO_BUILD_NEEDED:
        logging.warning(
            "export_and_scan_vulnerabilities called with build_mode=NO_BUILD_NEEDED"
        )
        return
    elif build_mode == BuildMode.RELEASE:
        _export_and_scan_vulnerabilities_cd(**kwargs)
    elif build_mode == BuildMode.NORMAL:
        _export_and_scan_vulnerabilities_ci(rebuild=False, **kwargs)
    elif build_mode == BuildMode.REBUILD:
        _export_and_scan_vulnerabilities_ci(rebuild=True, **kwargs)
    else:
        raise ValueError(f"Invalid build mode: {build_mode}")
