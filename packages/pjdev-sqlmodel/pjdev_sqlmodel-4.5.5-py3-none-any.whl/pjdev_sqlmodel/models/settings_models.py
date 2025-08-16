from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from abc import ABC, abstractmethod
from typing import TypeVar, Any, Dict
from sqlalchemy.pool import NullPool


class SqlModelSettings(BaseSettings, ABC):
    host: str
    db_name: str

    @abstractmethod
    def get_connection_string(self) -> str:
        pass

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_prefix="PJDEV_"
    )


class ConnectionOptions(BaseModel, ABC):
    echo: bool = False


TSettings = TypeVar(name="TSettings", bound=SqlModelSettings)
TOptions = TypeVar(name="TOptions", bound=ConnectionOptions)


class PostgresConnectionOptions(ConnectionOptions):
    pool_size: int = 5
    max_overflow: int = 10


class SqliteConnectionOptions(ConnectionOptions):
    connect_args: Dict[str, Any] = {"check_same_thread": False}
    poolclass: Any = NullPool


class MSSqlConnectionOptions(ConnectionOptions):
    pass


class MSSqlSettings(SqlModelSettings):
    use_trusted_connection: bool = False
    driver: int

    def get_connection_string(self) -> str:
        return f'mssql+pyodbc://{self.host}/{self.db_name}?driver=ODBC+Driver+{self.driver}+for+SQL+Server&Trusted_Connection={"yes" if self.use_trusted_connection else "no"}'


class SqliteSettings(SqlModelSettings):
    def get_connection_string(self) -> str:
        return f"sqlite:///{self.host}.{self.db_name}"


class PostgresSettings(SqlModelSettings):
    username: str
    password: str
    port: int = 5432

    def get_connection_string(self) -> str:
        return f"postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
