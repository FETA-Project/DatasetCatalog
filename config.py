from typing import Optional

from pydantic import BaseSettings


class KatodaConfig(BaseSettings):
    # STATIC_DIR = "frontend/.output/public"
    STATIC_DIR = "static"

    DATABASE_URL: Optional[str] = "localhost:27017"
    DATABASE_USER: Optional[str]
    DATABASE_PASS: Optional[str]
    DATABASE_NAME: Optional[str] = "katoda"

    # DATABASE_URI: str = f"mongodb://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_URL}"
    DATABASE_URI: Optional[str] = f"mongodb://{DATABASE_URL}"

    CLIENT_ORIGIN: Optional[str] = "http://localhost:8000"

    # ANALYSIS_DIR: Optional[str] = "./dataset_analysis"
    ANALYSIS_DIR: Optional[str] = "./katoda-test"
    DATASET_DIR: Optional[str] = "./datasets"

    # GIT_URL: Optional[str] = "https://gitlab.com/tranquiloSan/katoda-test"
    GIT_URL: Optional[str] = "https://gitlab.liberouter.org/monitoring/katoda-datasets"

    S3_URL: Optional[str] = "http://localhost:4566"
    S3_ACCESS_KEY: Optional[str] = "katoda"
    S3_SECRET_KEY: Optional[str] = "katoda"
    S3_USER: Optional[str] = "katoda"
    S3_BUCKET: Optional[str] = "katoda"

    DEV: Optional[bool] = False
    DEV_USER: Optional[str] = "test"

    class Config:
        # env_file = "./.env"
        env_file = "/etc/katoda/config.env", ".env"


config = KatodaConfig()
