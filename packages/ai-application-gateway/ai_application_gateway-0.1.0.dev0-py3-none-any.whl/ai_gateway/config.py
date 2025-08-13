import os

from dynaconf import Dynaconf
from lazify import LazyProxy
from loguru import logger

project_dir = os.path.dirname(os.path.abspath(__file__))
env = os.environ.get("ENV") or "dev"

logger.info(f"Environment variable: {env}")

settings_files = [
    os.path.join(project_dir, "settings.toml"),
    os.path.join(project_dir, f"settings.{env}.toml"),
    os.path.join(project_dir, f"settings.{env}.local.toml"),
]

def get_config():
    return Dynaconf(
        env=env,
        envvar_prefix="AAG",
        settings_files=settings_files,
        lowercase_read=True,
        environments=True,
        load_dotenv=True,
        dotenv_path=os.path.join(project_dir, ".env"),
    )


config = LazyProxy(get_config, enable_cache=True)
