import binascii
import enum
import json
import os
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import environ

from leaguemanager.core.toolbox import module_to_os_path

MODULE_NAME = "leaguemanager"
HOST_APP_DIR = module_to_os_path(MODULE_NAME)


def set_to_cwd_if_none(value: str) -> Path:
    """Set the user app directory."""
    if not value:
        return Path.cwd()
    try:
        return Path(value).resolve()
    except ValueError as e:
        raise ValueError(f"Invalid path for app_dir: {value}") from e


@environ.config
class HostApplication:
    app_name: str = MODULE_NAME
    app_dir: Path = environ.var(default=HOST_APP_DIR)
    root_dir: Path = environ.var(default=HOST_APP_DIR.parent.parent.resolve())
    db_services_dir: Path = environ.var(default=HOST_APP_DIR / "services")
    template_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "template_loader")
    schedule_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "scheduling")
    # db_config_dir: Path = environ.var(default=HOST_APP_DIR / "db" / "config")

    synth_data_dir: Path = environ.var(default=HOST_APP_DIR / "db" / "synthetic_data")

    excel_template_dir: Path = environ.var(default=HOST_APP_DIR / "db" / "importer_templates" / "excel")

    @environ.config(prefix="USER")
    class UserApplication:
        """User application settings."""

        app_name: str = environ.var(default=None)
        app_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        root_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_services_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_config_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)

    @environ.config(prefix="ALEMBIC")
    class AlembicConfig:
        """Configuration for Alembic migrations."""

        migration_path: Path = environ.var(default=None)
        migration_config_path: Path = environ.var(default=None)
        template_path: Path = environ.var(default=None)
        sqlite_data_directory: Path = environ.var(default=Path.cwd() / "data_league_db")

    user_app: UserApplication = environ.group(UserApplication)
    alembic: AlembicConfig = environ.group(AlembicConfig)


@lru_cache(maxsize=1)
def get_settings() -> HostApplication:
    """Get the settings for the host application."""
    return environ.to_config(HostApplication)


if __name__ == "__main__":
    settings = environ.to_config(HostApplication)

    print(environ.generate_help(HostApplication, display_defaults=True))
    print(settings.user_app.app_dir)
