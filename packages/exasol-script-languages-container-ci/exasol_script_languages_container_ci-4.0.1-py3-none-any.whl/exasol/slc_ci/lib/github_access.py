import os
from pathlib import Path


class GithubAccess:
    def __init__(self, github_output_var: str):
        self.github_output_var = github_output_var

    @property
    def _get_github_output_file(self):
        get_github_output_file = Path(os.getenv("GITHUB_OUTPUT"))
        return get_github_output_file

    def write_result(self, value: str):
        with open(self._get_github_output_file, "a") as f:
            f.write(f"{self.github_output_var}={value}\n")
