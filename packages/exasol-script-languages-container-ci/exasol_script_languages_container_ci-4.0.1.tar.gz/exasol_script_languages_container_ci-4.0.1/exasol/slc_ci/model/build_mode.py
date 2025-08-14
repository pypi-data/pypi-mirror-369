from enum import Enum


class BuildMode(Enum):
    """
    This enum serves as a definition of values for possible build modes.
    """

    NO_BUILD_NEEDED = "no_build_needed"
    NORMAL = "normal"
    REBUILD = "rebuild"
    RELEASE = "release"


def buildModeValues() -> list[str]:
    return [a.value for a in BuildMode]


def defaultBuildMode() -> BuildMode:
    return BuildMode.NORMAL
