from __future__ import annotations

from pathlib import Path

import nox
from nox import options

PATH_TO_PROJECT = Path() / "ongaku"
EXAMPLES_PATH = Path() / "examples"
EXAMPLE_FOLDERS = ["arc", "crescent", "hikari", "lightbulb", "tanjun"]
SCRIPT_PATHS = [
    PATH_TO_PROJECT,
    EXAMPLES_PATH,
    "noxfile.py",
    Path() / "tests",
]

options.default_venv_backend = "uv"
options.sessions = [
    "format_fix",
    "import_fix",
    "pyright",
    "pytest",
    "docs",
]


def uv_sync(
    session: nox.Session,
    *,
    groups: list[str] | None = None,
    extras: list[str] | None = None,
) -> None:
    group_set: set[str] = set(groups) if groups else set()
    extra_set: set[str] = set(extras) if extras else set()

    group_args: list[str] = []
    for group in group_set:
        group_args.extend(["--group", group])

    extra_args: list[str] = []
    for extra in extra_set:
        extra_args.extend(["--extra", extra])

    session.run_install(
        "uv",
        "sync",
        "--locked",
        *group_args,
        *extra_args,
        silent=True,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session()
def format_fix(session: nox.Session) -> None:
    uv_sync(session, groups=["format"])
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS)
    session.run("python", "-m", "ruff", "check", *SCRIPT_PATHS, "--fix")


@nox.session()
def import_fix(session: nox.Session) -> None:
    uv_sync(session, groups=["format"])
    session.run(
        "python",
        "-m",
        "ruff",
        "check",
        "--select",
        "I",
        *SCRIPT_PATHS,
        "--fix",
    )
    session.run("python", "-m", "ruff", "format", *SCRIPT_PATHS)


@nox.session()
def format_check(session: nox.Session) -> None:
    uv_sync(session, groups=["format"])
    session.run("ruff", "check", "--output-format=github")


@nox.session()
def pyright(session: nox.Session) -> None:
    uv_sync(session, groups=["dev", "examples"], extras=["injection", "speedups"])
    session.run("pyright", PATH_TO_PROJECT, EXAMPLES_PATH)


@nox.session()
def pytest(session: nox.Session) -> None:
    uv_sync(session, groups=["test"], extras=["injection", "speedups"])
    session.run("pytest", "tests")


@nox.session()
def docs(session: nox.Session) -> None:
    uv_sync(session, groups=["doc"])
    session.run("python", "-m", "mkdocs", "build", "-q", "-s")


@nox.session()
def servedocs(session: nox.Session) -> None:
    uv_sync(session, groups=["doc"])
    session.run("python", "-m", "mkdocs", "serve")
