# database-url
![Python Versions](https://img.shields.io/pypi/pyversions/tortoise-database-url)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/tortoise-database-url.svg?style=flat)](https://pypi.org/project/tortoise-database-url/)
[![GithubActionResult](https://github.com/waketzheng/database-url/workflows/ci/badge.svg)](https://github.com/waketzheng/database-url/actions?query=workflow:ci)
[![Coverage Status](https://coveralls.io/repos/github/waketzheng/database-url/badge.svg?branch=main)](https://coveralls.io/github/waketzheng/database-url?branch=main)
![Mypy coverage](https://img.shields.io/badge/mypy-100%25-green.svg)

Toolkit for TortoiseORM to generate database url from Django DATABASES item format.

## Installation

```bash
pip install tortoise-database-url
```
Or by uv/pdm:
```bash
uv add tortoise-database-url
pdm add tortoise-database-url
```

## Usage

- DbUrl
```py
from tortoise_database_url import DbUrl

db_url = DbUrl.mysql('my_db', user='root', password='Me@example.com')
print(db_url)
# mysql://root:Me%40example.com@127.0.0.1:3306/my_db
```

- generate

```py
import tortoise_database_url

db_url = tortoise_database_url.generate('my_db', engine='mysql', user='root', password='Me@example.com')
print(db_url)
# mysql://root:Me%40example.com@127.0.0.1:3306/my_db

db_url = tortoise_database_url.generate('db_name', engine='postgres')
print(db_url)
# postgres://postgres:postgres@127.0.0.1:5432/db_name
```

- from_django_item
```py
import pathlib
import tortoise_database_url

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": pathlib.Path("/tmp") / "db.sqlite3"
    },
}

db_url = tortoise_database_url.from_django_item(DATABASES["default"])
print(db_url)
# sqlte:///tmp/db.sqlite3
```
See more at:
https://github.com/waketzheng/database-url/blob/main/tests/test_main.py
https://tortoise.github.io/databases.html?h=database
