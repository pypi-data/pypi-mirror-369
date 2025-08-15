# -*- coding: utf-8 -*-
import os
from typing import Optional, Tuple, Literal
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

env_file = ".env"
env_example_file = ".env.example"

# Load the appropriate .env file
if os.path.exists(env_file):
    load_dotenv(env_file)
elif os.path.exists(env_example_file):
    load_dotenv(env_example_file)


class Settings(BaseSettings):
    """Runtime Manager Service Settings"""

    # Service settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1
    DEBUG: bool = False
    BEARER_TOKEN: Optional[str] = None

    # Runtime Manager settings
    DEFAULT_SANDBOX_TYPE: str = "base"
    WORKDIR: str = "/workspace"
    POOL_SIZE: int = 1
    AUTO_CLEANUP: bool = True
    CONTAINER_PREFIX_KEY: str = "runtime_sandbox_container_"
    CONTAINER_DEPLOYMENT: Literal["docker", "cloud"] = "docker"
    DEFAULT_MOUNT_DIR: str = "sessions_mount_dir"
    STORAGE_FOLDER: str = "runtime_sandbox_storage"
    PORT_RANGE: Tuple[int, int] = (49152, 59152)

    # Redis settings
    REDIS_ENABLED: bool = False
    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USER: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PORT_KEY: str = "_runtime_sandbox_container_occupied_ports"
    REDIS_CONTAINER_POOL_KEY: str = "_runtime_sandbox_container_container_pool"

    # OSS settings
    FILE_SYSTEM: Literal["local", "oss"] = "local"
    OSS_ENDPOINT: str = "http://oss-cn-hangzhou.aliyuncs.com"
    OSS_ACCESS_KEY_ID: str = "your-access-key-id"
    OSS_ACCESS_KEY_SECRET: str = "your-access-key-secret"
    OSS_BUCKET_NAME: str = "your-bucket-name"

    class Config:
        env_file = env_file if os.path.exists(env_file) else env_example_file
        case_sensitive = True

    @field_validator("WORKERS", mode="before")
    @classmethod
    def validate_workers(cls, value, info):
        if not info.data.get("REDIS_ENABLED", False):
            return 1
        return value


settings = Settings()
