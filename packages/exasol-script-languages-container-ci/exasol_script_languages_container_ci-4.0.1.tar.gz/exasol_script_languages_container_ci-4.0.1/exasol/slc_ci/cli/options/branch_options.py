import click

branch_option = click.option(
    "--branch-name",
    type=str,
    required=True,
    help="In case of a PR, the source branch of the PR.",
)

base_branch_option = click.option(
    "--base-ref",
    type=str,
    required=True,
    help="In case of a PR, the target ref of the PR.",
)

commit_sha_option = click.option(
    "--commit-sha",
    type=str,
    required=True,
    help="Commit sha that trigger the GH event",
)

remote_option = click.option(
    "--remote",
    type=str,
    default="origin",
    required=False,
    help="The remote Git repository of the base branch",
)
