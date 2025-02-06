from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    STATIC_DIR = "frontend/.output/public"

    DATABASE_URL: Optional[str] = "localhost:27017"
    DATABASE_USER: Optional[str]
    DATABASE_PASS: Optional[str]
    DATABASE_NAME: Optional[str] = 'catalogDB'

    # DATABASE_URI: str = f"mongodb://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_URL}"
    DATABASE_URI: Optional[str] = f"mongodb://{DATABASE_URL}"

    JWT_PRIVATE_KEY: Optional[str] = ""
    JWT_PUBLIC_KEY: Optional[str] = ""

    REFRESH_TOKEN_EXPIRES_IN: Optional[int] = 3600*24*7
    ACCESS_TOKEN_EXPIRES_IN: Optional[int] = 3600
    JWT_ALGORITHM: Optional[str] = "RS256"

    CLIENT_ORIGIN: Optional[str] = "http://localhost:3000"

    # ANALYSIS_DIR: Optional[str] = "./dataset_analysis"
    ANALYSIS_DIR: Optional[str] = "./katoda-test"
    DATASET_DIR: Optional[str] = "./datasets"

    # GIT_URL: Optional[str] = "https://gitlab.com/tranquiloSan/katoda-test"
    GIT_URL: Optional[str] = "https://gitlab.liberouter.org/monitoring/katoda-datasets"

    S3_URL: Optional[str] = "https://s3.liberouter.org"
    S3_ACCESS_KEY: Optional[str] = "katoda"
    S3_SECRET_KEY: Optional[str] = "katoda"
    S3_USER: Optional[str] = "katoda"

    class Config:
        env_file = './.env'


config = Config()
