from enum import Enum


class GithubEvent(Enum):
    """
    This enum serves as a definition of values for possible github events.
    """

    PULL_REQUEST = "pull_request"
    PUSH = "push"


def githubEventValues() -> list[str]:
    return [a.value for a in GithubEvent]
