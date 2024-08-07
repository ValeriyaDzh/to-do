import logging
from logging.config import dictConfig
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

load_dotenv()


class DatabaseSettings(BaseSettings):

    PROTOCOL: str
    HOST: str
    PORT: int
    NAME: str
    USER: str
    PASSWORD: SecretStr

    model_config = SettingsConfigDict(extra="ignore", env_prefix="DB_")

    @property
    def URL(self):
        return SecretStr(
            f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class LoggerSettings(BaseSettings):

    LEVEL: str
    FILE: str
    IGNORED_LOGGERS: list[str] = ["passlib", "asyncio"]
    IGNORED_LOGGERS_LEVEL: str = "ERROR"

    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")

    def configure_logging(self):
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                    },
                },
                "handlers": {
                    "file": {
                        "level": self.LEVEL,
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": self.FILE,
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["file"],
                        "level": self.LEVEL,
                        "propagate": False,
                    },
                },
            }
        )

        for log in self.IGNORED_LOGGERS:
            self._set_level(log, self.IGNORED_LOGGERS_LEVEL)

    @staticmethod
    def _set_level(logger: str, level: str):
        logging.getLogger(logger).setLevel(level)


class Settings(BaseSettings):

    db: DatabaseSettings = DatabaseSettings()
    log: LoggerSettings = LoggerSettings()


settings = Settings()
