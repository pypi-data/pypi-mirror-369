import os
from typing import Dict, List, Optional

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    SONA_DEBUG: bool = False

    SONA_INFERENCER_CLASS: Optional[str] = None

    # Core Storage settings
    SONA_STORAGE_LOCAL_PATH: str = os.getcwd()
    SONA_STORAGE_S3_SETTING: Dict = dict()
    SONA_STORAGE_S3_BUCKET: str = "sona"

    SONA_STORAGE_GOOGLE_CREDENTIAL: Optional[Dict] = None
    SONA_STORAGE_GOOGLE_BUCKET: str ="sona"

    SONA_STORAGE_AZURE_ENDPOINT: Optional[str] = None
    SONA_STORAGE_AZURE_ACCOUNT_NAME: Optional[str] = None
    SONA_STORAGE_AZURE_ACCOUNT_KEY: Optional[str] = None
    SONA_STORAGE_AZURE_CONTAINER: str = "sona"

    # Worker base settings
    SONA_WORKER_CLASS: str = "sona.worker.workers.InferencerWorker"
    SONA_WORKER_TOPIC_PREFIX: str = "sona.inferencer."
    SONA_WORKER_TOPIC: Optional[str] = None

    # Worker consumer settings
    SONA_WORKER_CONSUMER_SQS_SETTING: Optional[Dict] = None
    SONA_WORKER_CONSUMER_KAFKA_SETTING: Optional[Dict] = None
    SONA_WORKER_CONSUMER_REDIS_URL: Optional[RedisDsn] = None
    SONA_WORKER_CONSUMER_REDIS_GROUP: Optional[str] = "sona.anonymous"
    SONA_WORKER_CONSUMER_AZURE_ENDPOINT: Optional[str] = None
    SONA_WORKER_CONSUMER_AZURE_ACCOUNT_NAME: Optional[str] = None
    SONA_WORKER_CONSUMER_AZURE_ACCOUNT_KEY: Optional[str] = None

    # Worker producer settings
    SONA_WORKER_PRODUCER_SQS_SETTING: Optional[Dict] = None
    SONA_WORKER_PRODUCER_KAFKA_SETTING: Optional[Dict] = None
    SONA_WORKER_PRODUCER_REDIS_URL: Optional[RedisDsn] = None
    SONA_WORKER_PRODUCER_AZURE_ENDPOINT: Optional[str] = None
    SONA_WORKER_PRODUCER_AZURE_ACCOUNT_NAME: Optional[str] = None
    SONA_WORKER_PRODUCER_AZURE_ACCOUNT_KEY: Optional[str] = None

    # Middleware settings
    SONA_MIDDLEWARE_CLASSES: List[str] = []
    SONA_MIDDLEWARE_SUPERVISOR_SQS_SETTING: Optional[Dict] = None
    SONA_MIDDLEWARE_SUPERVISOR_KAFKA_SETTING: Optional[Dict] = None

    # Streaming Settings
    SONA_STREAM_INFERENCER_CLASS: Optional[str] = None
    SONA_STREAM_PROCESS_LIMIT: int = 10
    SONA_STREAM_RTC_STUNNER_AUTH_URL: Optional[str] = None
    SONA_STREAM_RTC_TURN_FDQN: Optional[str] = None
    SONA_STREAM_RTC_USER: Optional[str] = None
    SONA_STREAM_RTC_PASS: Optional[str] = None

    SONA_STREAM_SIDECAR_SHARED_PATH: Optional[str] = None
    SONA_STREAM_SIDECAR_SUPERVISOR_TOPICS: List = []


settings = Settings()
