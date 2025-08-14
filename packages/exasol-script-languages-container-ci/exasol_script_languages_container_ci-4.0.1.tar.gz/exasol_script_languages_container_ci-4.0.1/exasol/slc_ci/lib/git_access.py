from collections.abc import Iterable

from git import Repo


class GitAccess:

    def get_last_commit_message(self):
        """
        Assumes that PWD belongs to a GIT repository. Get's the last commit message of this repo and returns it as string
        :return: Last commit message of current working directory GIT repository.
        """
        return Repo().head.commit.message

    def get_head_commit_sha_of_branch(self, branch_name) -> str:
        """
        Returns the last commit sha of given branch.
        :raise: ValueError: if the refs with label 'branch_name' does not exists or is not unique.
        """
        repo = Repo()
        branch = [b for b in repo.refs if b.name == branch_name]  # type: ignore
        if len(branch) == 0:
            ex_msg = f"Branch '{branch_name}' does not exist."
            raise ValueError(ex_msg)
        elif len(branch) > 1:
            ex_msg = f"Branch '{branch_name}' found more than once."
            raise ValueError(ex_msg)
        return str(branch[0].commit)

    def get_last_commits(self) -> Iterable[str]:
        """
        Returns all commit-sha's of the current branch of the repo in the cwd.
        """
        repo = Repo()
        for c in repo.iter_commits(repo.head):
            yield str(c)

    def get_files_of_commit(self, commit_sha) -> Iterable[str]:
        """
        Returns the files of the specific commits of the repo in the cwd.
        """
        repo = Repo()
        return repo.commit(commit_sha).stats.files.keys()  # type: ignore
