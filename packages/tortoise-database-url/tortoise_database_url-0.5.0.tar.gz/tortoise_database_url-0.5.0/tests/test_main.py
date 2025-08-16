from __future__ import annotations

import os
from pathlib import Path

import pytest

from tortoise_database_url import (
    DbDefaultParams,
    DbUrl,
    EngineEnum,
    InvalidEngine,
    from_django_item,
    generate,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES: dict[str, dict] = {
    "default": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": "xe",
        "USER": "a_user",
        "PASSWORD": "a_password",
        "HOST": "dbprod01ned.mycompany.com",
        "PORT": "1540",
    },
    "MySQL/MariaDB": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test_1",
    },
    "psql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": None,
    },
    "oracle": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": "",
    },
    "sqlite": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.db"},
    "complex_password": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "foo",
        "PASSWORD": "Hello@world",
    },
    "quoted_password": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "foo",
        "PASSWORD": "Hello%40world",
    },
}


def test_django_item() -> None:
    assert (
        from_django_item(DATABASES["default"])
        == "oracle://a_user:a_password@dbprod01ned.mycompany.com:1540/xe"
    )
    assert (
        from_django_item(DATABASES["MySQL/MariaDB"]) == "mysql://root:123456@127.0.0.1:3306/test_1"
    )
    assert from_django_item(DATABASES["psql"]) == "postgres://postgres:postgres@127.0.0.1:5432/None"
    assert from_django_item(DATABASES["oracle"]) == "oracle://SYSTEM:123456@127.0.0.1:1521/"
    assert from_django_item(DATABASES["sqlite"]) == f"sqlite://{BASE_DIR / 'test.db'}"
    assert (
        from_django_item(DATABASES["complex_password"])
        == from_django_item(DATABASES["quoted_password"])
        == "mysql://root:Hello%40world@127.0.0.1:3306/foo"
    )


def test_generate() -> None:
    assert generate(None) == "sqlite://:memory:"
    assert generate() == "sqlite://db.sqlite3"
    assert generate(BASE_DIR / "db.sqlite3") == f"sqlite://{BASE_DIR / 'db.sqlite3'}"

    # postgresql
    default_postgres_port: int = DbDefaultParams.postgres[-1]
    assert (
        generate("my_db", engine="postgres")
        == generate("my_db", engine="postgresql")
        == (f"postgres://postgres:postgres@127.0.0.1:{default_postgres_port}/my_db")
    )
    assert generate("my_db", engine="asyncpg") == (
        f"asyncpg://postgres:postgres@127.0.0.1:{default_postgres_port}/my_db"
    )
    assert generate("my_db", engine="psycopg") == (
        f"psycopg://postgres:postgres@127.0.0.1:{default_postgres_port}/my_db"
    )

    # MySQL & MariaDB
    default_mysql_port: int = DbDefaultParams.mysql[-1]
    assert (
        generate("my_db", engine="mysql")
        == generate("my_db", engine="mariadb")
        == (f"mysql://root:123456@127.0.0.1:{default_mysql_port}/my_db")
    )

    # Other
    assert generate("test_db", "mssql") == "mssql://sa:Abcd12345678@127.0.0.1:1432/test_db"
    assert (
        generate("test_db", "mssql", driver="ODBC Driver 18 for SQL Server")
        == "mssql://sa:Abcd12345678@127.0.0.1:1432/test_db?driver=ODBC Driver 18 for SQL Server"
    )
    assert generate("test_db", engine="oracle") == "oracle://SYSTEM:123456@127.0.0.1:1521/test_db"

    with pytest.raises(InvalidEngine):
        generate(engine="mongo")  # type:ignore


def test_generate_with_env(monkeypatch) -> None:
    monkeypatch.setenv("DB_USER", "admin")
    monkeypatch.setenv("DB_PASS", "secret@")
    monkeypatch.setenv("DB_HOST", "db.mydomain.com")
    monkeypatch.setenv("DB_PORT", "5555")
    db_url = generate(
        "my_db",
        engine="postgres",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    assert db_url == "postgres://admin:secret%40@db.mydomain.com:5555/my_db"

    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASS", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    db_url = generate(
        "my_db",
        engine="postgres",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    assert db_url == "postgres://postgres:postgres@127.0.0.1:5432/my_db"
    db_url = generate(
        "my_db",
        engine=EngineEnum.postgres,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    assert db_url == "postgres://postgres:postgres@127.0.0.1:5432/my_db"


class TestDbUrl:
    def test_postgres(self):
        db_url = DbUrl.postgres("my_db")
        assert db_url == "postgres://postgres:postgres@127.0.0.1:5432/my_db"

    def test_mysql(self):
        db_url = DbUrl.mysql("test_1")
        assert db_url == "mysql://root:123456@127.0.0.1:3306/test_1"

    def test_sqlite(self):
        assert DbUrl.sqlite(None) == DbUrl.MEMORY_SQLITE
        assert DbUrl.sqlite("") == DbUrl.DJANGO_DEFAULT_SQLITE
        assert DbUrl.sqlite("my-file") == "sqlite://my-file"

    def test_build_url(self):
        assert (
            DbUrl.build_url("test_db", DbUrl.Engines.oracle)
            == "oracle://SYSTEM:123456@127.0.0.1:1521/test_db"
        )
