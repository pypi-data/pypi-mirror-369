from exasol.slc_ci.lib.ci_prepare import CIPrepare
from exasol.slc_ci.lib.ci_push_test_container import CIPushTestContainer
from exasol.slc_ci.lib.get_build_config_model import get_build_config_model


def prepare_test_container(
    docker_user: str,
    docker_password: str,
    commit_sha: str,
    ci_prepare: CIPrepare,
    ci_push_test_container: CIPushTestContainer,
) -> None:
    build_config = get_build_config_model()
    ci_prepare.prepare(commit_sha=commit_sha)

    ci_push_test_container.push_test_container(
        build_docker_repository=build_config.docker_build_repository,
        force=True,
        commit_sha=commit_sha,
        docker_user=docker_user,
        docker_password=docker_password,
        test_container_folder=build_config.test_container_folder,
    )
