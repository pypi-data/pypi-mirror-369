from argparse import Namespace
from inspect import stack
from os import environ

from wowool.portal.client.defines import (
    WOWOOL_PORTAL_API_KEY_ENV_NAME,
    WOWOOL_PORTAL_HOST_DEFAULT,
    WOWOOL_PORTAL_HOST_ENV_NAME,
)
from wowool.portal.client.error import PortalClientError


def apply_environment_host(arguments: Namespace):
    # Host
    env_host = environ[WOWOOL_PORTAL_HOST_ENV_NAME] if WOWOOL_PORTAL_HOST_ENV_NAME in environ else None
    host = arguments.host if arguments.host else env_host
    if not host:
        host = WOWOOL_PORTAL_HOST_DEFAULT
    if host.endswith("/"):
        host = host[:-1]
    arguments.host = host


def apply_environment_api_key(arguments: Namespace, empty_ok=False):
    # API key
    env_api_key = environ[WOWOOL_PORTAL_API_KEY_ENV_NAME] if WOWOOL_PORTAL_API_KEY_ENV_NAME in environ else None
    arguments.api_key = arguments.api_key if arguments.api_key else env_api_key
    if not empty_ok and arguments.api_key is None:
        raise PortalClientError(
            "MissingApiKeyError",
            f"An API key is required. Use the -k option or set the environment variable '{WOWOOL_PORTAL_API_KEY_ENV_NAME}'",
        )


def apply_environment_variables(arguments: Namespace):
    apply_environment_host(arguments)
    apply_environment_api_key(arguments)


def find_variable(variable_name: str):
    try:
        for frame_info in stack():
            frame = frame_info.frame
            module_name = frame.f_globals.get("__name__")
            # Skip internal calls from our own modules
            if module_name not in ("wowool.portal.client.environment", "wowool.portal.client.pipeline"):
                value = frame.f_globals.get(variable_name, None)
                if value is not None:
                    return value
    finally:
        del frame  # Avoid reference cycles


def resolve_variable(variable_name, default: str | None = None) -> str:
    variable = find_variable(variable_name)
    if variable is not None:
        return variable
    value = environ.get(variable_name, default)
    if value is None:
        raise PortalClientError("ConfigurationError", f"Environment variable '{variable_name}' is not set and no default value provided.")
    return value
