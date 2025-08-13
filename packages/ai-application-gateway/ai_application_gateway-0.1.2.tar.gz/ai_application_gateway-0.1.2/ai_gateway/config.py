import os

from dynaconf import Dynaconf
from lazify import LazyProxy
from loguru import logger

project_dir = os.path.dirname(os.path.abspath(__file__))

env_file_path = os.environ.get("ENV_FILE_PATH")
if env_file_path:
    dotenv_path_str = env_file_path
else:
    dotenv_path_str = os.path.join(project_dir, ".env")

env = os.environ.get("ENV") or "dev"

logger.info(f"Environment variable: {env}")

settings_files = [
    os.path.join(project_dir, "settings.toml"),
    os.path.join(project_dir, f"settings.{env}.toml"),
    os.path.join(project_dir, f"settings.{env}.local.toml"),
]

settings_file_path = os.environ.get("SETTINGS_FILE_PATH")
if settings_file_path:
    settings_files.append(settings_file_path)

def get_config():
    return Dynaconf(
        env=env,
        envvar_prefix="AAG",
        settings_files=settings_files,
        lowercase_read=True,
        environments=True,
        load_dotenv=True,
        dotenv_path=dotenv_path_str,
    )


config = LazyProxy(get_config, enable_cache=True)
