"""
This module provides methods to load environment variables dynamically.
"""

import os

from dotenv import dotenv_values, load_dotenv


def load_env(env_override: str = None):
    """
    Load environment variables from files using explicit paths.

    Args:
        env_override: Optional environment to load ('local' or 'test').
                      Loads .env first, then overrides based on env_override or env vars.
    """
    assert env_override in [None, "local", "test"], "Invalid environment specified"

    # Always load the default .env file first
    load_dotenv(".env")

    # Load the appropriate environment overrides if necessary using explicit paths
    if env_override == "test" or os.environ.get("TEST") == "1":
        # If TEST=1 is set or env is 'test', load .env.test
        load_dotenv(".env.test", override=True)
    elif env_override == "local" or os.environ.get("LOCAL") == "1":
        # If LOCAL=1 is set or env is 'local', load .env.local to override values
        load_dotenv(".env.local", override=True)


def get_env_var_keys():
    """
    Get environment variable keys from .env
    """
    return dotenv_values(".env").keys()
