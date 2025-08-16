from __future__ import annotations

import re
from dataclasses import dataclass
from enum import auto
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote_plus

from asynctor.compat import StrEnum


class DatabaseUrlError(Exception): ...


class InvalidEngine(DatabaseUrlError): ...


@dataclass
class DbDefaultParams:
    """Db param tuple -- username, password, port"""

    postgres: tuple[str, str, int] = "postgres", "postgres", 5432
    mysql: tuple[str, str, int] = "root", "123456", 3306
    mssql: tuple[str, str, int] = "sa", "Abcd12345678", 1432
    oracle: tuple[str, str, int] = "SYSTEM", "123456", 1521


class EngineEnum(StrEnum):
    sqlite = auto()
    mysql = auto()
    postgres = auto()
    mssql = auto()
    oracle = auto()


def should_quote(value: str) -> bool:
    return not re.match(r"[-%\w]+$", value)


def generate(
    name: Path | str | None = "db.sqlite3",
    engine: EngineEnum
    | Literal[
        "sqlite",
        "postgres",
        "mysql",
        "postgres",
        "mssql",
        "oracle",
        "sqlite3",
        "asyncpg",
        "psycopg",
        "postgresql",
        "mariadb",
    ] = "sqlite",
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    port: str | int | None = None,
    **extras: Any,
) -> str:
    """Generate db url with password quoted

    :param name: database name, if None and engine is sqlite, it will be :memory:
    :param engine: connection engine that supported by tortoise-orm
    :param host: db host, default is '127.0.0.1'
    :param user: db user, default to be value of DbDefaultEnum
    :param password: db password, default to be value of DbDefaultEnum
    :param port: db port, default to be value of DbDefaultEnum
    :param extras: kwargs that will be appended behind '?'

    Usage::
        >>> generate('mydb', engine='postgres', password='me@qq.com')
        'postgres://postgres:me%40qq.com@127.0.0.1:5432/mydb'
    """
    if isinstance(engine, EngineEnum):
        return _generate(name, engine.name, host, user, password, port, **extras)
    return _generate(name, engine, host, user, password, port, **extras)


def _generate(
    name: Path | str | None = "db.sqlite3",
    engine: str = "sqlite",
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    port: str | int | None = None,
    **extras: Any,
) -> str:
    if engine == "sqlite" or (engine := engine.split(".")[-1]) in ("sqlite", "sqlite3"):
        if name is None:
            name = ":memory:"
        return f"sqlite://{name}"
    if engine in (
        "postgres",
        "asyncpg",
        "psycopg",
        "postgresql",
    ):
        engine = engine.replace("postgresql", "postgres")
        default_user, default_pw, default_port = DbDefaultParams.postgres
    elif engine in ("mysql", "mariadb"):
        engine = "mysql"
        default_user, default_pw, default_port = DbDefaultParams.mysql
    elif engine == "mssql":
        default_user, default_pw, default_port = DbDefaultParams.mssql
    elif engine == "oracle":
        default_user, default_pw, default_port = DbDefaultParams.oracle
    else:
        raise InvalidEngine(engine)
    if port is None:
        port = default_port
    if host is None:
        host = "127.0.0.1"
    if user is None:
        user = default_user
    if password is None:
        password = default_pw
    elif should_quote(password):
        password = quote_plus(password)
    url = f"{engine}://{user}:{password}@{host}:{port}/{name}"
    if extras:
        url += "?" + "&".join(f"{k}={v}" for k, v in extras.items())
    return url


def from_django_item(default: dict[str, Any]) -> str:
    """Convert Django database to tortoie db_url format

    Example::
    ```py
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3"
        },
    }

    db_url = database_url.from_django_item(DATABASES["default"])
    print(db_url)
    # sqlte:////db.sqlite3
    """
    return _generate(**{k.lower(): v for k, v in default.items()})


class DbUrl:
    MEMORY_SQLITE = "sqlite://:memory:"
    DJANGO_DEFAULT_SQLITE = "sqlite://db.sqlite3"
    Engines = EngineEnum

    @staticmethod
    def build_url(name: str, engine: EngineEnum, **kw: Any) -> str:
        return _generate(name, engine, **kw)

    @classmethod
    def mysql(cls, name: str, **kw: Any) -> str:
        return cls.build_url(name, cls.Engines.mysql, **kw)

    @classmethod
    def postgres(cls, name: str, **kw: Any) -> str:
        return cls.build_url(name, cls.Engines.postgres, **kw)

    @classmethod
    def sqlite(cls, file: str | None = None, **kw: Any) -> str:
        if file is None:
            return cls.MEMORY_SQLITE
        elif not file:
            return cls.DJANGO_DEFAULT_SQLITE
        return _generate(file, **kw)
