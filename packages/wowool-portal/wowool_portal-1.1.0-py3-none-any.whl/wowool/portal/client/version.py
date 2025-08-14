def get_version() -> str:
    import pkg_resources

    try:
        version = pkg_resources.require("wowool-portal")[0].version
    except pkg_resources.DistributionNotFound:
        from wowool.build.git import get_version

        version = get_version()
    return version
