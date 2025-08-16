import subprocess  # nosec
from pathlib import Path

from tortoise_database_url import __version__


def test_version():
    r = subprocess.run(["pdm", "list", "--fields=name,version", "--csv"], capture_output=True)
    out = r.stdout.decode().strip()
    try:
        me = [j for i in out.splitlines() if (j := i.split(","))[0] == "tortoise-database-url"][0]
    except IndexError:
        # TODO: remove this when deps of python3.14 can be install by pdm in ci
        assert __version__ in Path("src/tortoise_database_url/__init__.py").read_text()
    else:
        assert me[-1] == __version__
