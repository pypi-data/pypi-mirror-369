import json

from exasol.slc_ci.lib.get_build_config_model import get_build_config_model
from exasol.slc_ci.lib.get_flavor_ci_model import get_flavor_ci_model
from exasol.slc_ci.lib.github_access import GithubAccess
from exasol.slc_ci.model.flavor_ci_model import FlavorCiConfig, TestSet


def _build_test_matrix_entry(flavor_config: FlavorCiConfig, test_set: TestSet) -> dict:
    return {
        "test-set-name": test_set.name,
        "test-runner": (
            test_set.test_runner
            if test_set.test_runner
            else flavor_config.test_config.default_test_runner
        ),
        "goal": test_set.goal,
    }


def get_test_matrix(flavor: str, github_access: GithubAccess):
    build_config = get_build_config_model()
    flavor_config = get_flavor_ci_model(build_config, flavor)
    test_matrix = {
        "include": [
            _build_test_matrix_entry(flavor_config, entry)
            for entry in flavor_config.test_config.test_sets
        ]
    }
    github_access.write_result(json.dumps(test_matrix))
