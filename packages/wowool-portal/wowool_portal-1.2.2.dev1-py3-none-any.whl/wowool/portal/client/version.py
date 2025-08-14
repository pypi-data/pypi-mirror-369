from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    try:
        return version("wowool-portal")
    except PackageNotFoundError:
        from wowool.build.git import get_version as get_git_version

        return get_git_version()
