"""
Invoke - Tasks
==============
"""

from __future__ import annotations

import contextlib
import fnmatch
import inspect
import os
import re
import uuid
from itertools import chain
from textwrap import TextWrapper
from typing import TYPE_CHECKING

try:
    import biblib.bib
except ImportError:
    biblib = None
from invoke.tasks import task

import colour_cxf

if TYPE_CHECKING:
    from collections.abc import Callable

    from invoke.context import Context

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec  # pyright: ignore

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "APPLICATION_NAME",
    "APPLICATION_VERSION",
    "PYTHON_PACKAGE_NAME",
    "PYPI_PACKAGE_NAME",
    "PYPI_ARCHIVE_NAME",
    "BIBLIOGRAPHY_NAME",
    "clean",
    "formatting",
    "quality",
    "precommit",
    "tests",
    "examples",
    "preflight",
    "docs",
    "todo",
    "requirements",
    "build",
    "virtualise",
    "tag",
    "release",
    "sha256",
]

APPLICATION_NAME: str = colour_cxf.__application_name__

APPLICATION_VERSION: str = colour_cxf.__version__

PYTHON_PACKAGE_NAME: str = colour_cxf.__name__

PYPI_PACKAGE_NAME: str = "colour-cxf"
PYPI_ARCHIVE_NAME: str = PYPI_PACKAGE_NAME.replace("-", "_")

BIBLIOGRAPHY_NAME: str = "BIBLIOGRAPHY.bib"


def message_box(
    message: str,
    width: int = 79,
    padding: int = 3,
    print_callable: Callable = print,
) -> None:
    """
    Print a message inside a box.

    Parameters
    ----------
    message
        Message to print.
    width
        Message box width.
    padding
        Padding on each side of the message.
    print_callable
        Callable used to print the message box.

    Examples
    --------
    >>> message = (
    ...     "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    ...     "sed do eiusmod tempor incididunt ut labore et dolore magna "
    ...     "aliqua."
    ... )
    >>> message_box(message, width=75)
    ===========================================================================
    *                                                                         *
    *   Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do       *
    *   eiusmod tempor incididunt ut labore et dolore magna aliqua.           *
    *                                                                         *
    ===========================================================================
    >>> message_box(message, width=60)
    ============================================================
    *                                                          *
    *   Lorem ipsum dolor sit amet, consectetur adipiscing     *
    *   elit, sed do eiusmod tempor incididunt ut labore et    *
    *   dolore magna aliqua.                                   *
    *                                                          *
    ============================================================
    >>> message_box(message, width=75, padding=16)
    ===========================================================================
    *                                                                         *
    *                Lorem ipsum dolor sit amet, consectetur                  *
    *                adipiscing elit, sed do eiusmod tempor                   *
    *                incididunt ut labore et dolore magna                     *
    *                aliqua.                                                  *
    *                                                                         *
    ===========================================================================
    """

    ideal_width = width - padding * 2 - 2

    def inner(text: str) -> str:
        """Format and pads inner text for the message box."""

        return (
            f'*{" " * padding}'
            f'{text}{" " * (width - len(text) - padding * 2 - 2)}'
            f'{" " * padding}*'
        )

    print_callable("=" * width)
    print_callable(inner(""))

    wrapper = TextWrapper(
        width=ideal_width, break_long_words=False, replace_whitespace=False
    )

    lines = [wrapper.wrap(line) for line in message.split("\n")]
    for line in chain(*[" " if len(line) == 0 else line for line in lines]):
        print_callable(inner(line.expandtabs()))

    print_callable(inner(""))
    print_callable("=" * width)


@task
def clean(
    ctx: Context,
    docs: bool = True,
    bytecode: bool = False,
    pytest: bool = True,
) -> None:
    """
    Clean the project.

    Parameters
    ----------
    ctx
        Context.
    docs
        Whether to clean the *docs* directory.
    bytecode
        Whether to clean the bytecode files, e.g., *.pyc* files.
    pytest
        Whether to clean the *Pytest* cache directory.
    """

    message_box("Cleaning project...")

    patterns = ["build", "*.egg-info", "dist"]

    if docs:
        patterns.append("docs/_build")
        patterns.append("docs/generated")

    if bytecode:
        patterns.append("**/__pycache__")
        patterns.append("**/*.pyc")

    if pytest:
        patterns.append(".pytest_cache")

    for pattern in patterns:
        ctx.run(f"rm -rf {pattern}")


@task
def formatting(
    ctx: Context,
    asciify: bool = True,
    bibtex: bool = True,
) -> None:
    """
    Convert unicode characters to ASCII and cleanup the *BibTeX* file.

    Parameters
    ----------
    ctx
        Context.
    asciify
        Whether to convert unicode characters to ASCII.
    bibtex
        Whether to cleanup the *BibTeX* file.
    """

    if asciify:
        message_box("Converting unicode characters to ASCII...")
        with ctx.cd("utilities"):
            ctx.run("./unicode_to_ascii.py")

    if bibtex:
        message_box('Cleaning up "BibTeX" file...')
        if biblib is None:
            message_box("Warning: biblib module not available, skipping BibTeX cleanup")
        else:
            bibtex_path = BIBLIOGRAPHY_NAME
            with open(bibtex_path) as bibtex_file:
                entries = biblib.bib.Parser().parse(bibtex_file.read()).get_entries()

            for entry in sorted(entries.values(), key=lambda x: x.key):
                with contextlib.suppress(KeyError):
                    del entry["file"]

                for key, value in entry.items():
                    entry[key] = re.sub("(?<!\\\\)\\&", "\\&", value)

            with open(bibtex_path, "w") as bibtex_file:
                for entry in sorted(entries.values(), key=lambda x: x.key):
                    bibtex_file.write(entry.to_bib())
                    bibtex_file.write("\n")


@task
def quality(
    ctx: Context,
    pyright: bool = True,
    rstlint: bool = True,
) -> None:
    """
    Check the codebase with *Pyright* and lints various *restructuredText*
    files with *rst-lint*.

    Parameters
    ----------
    ctx
        Context.
    pyright
        Whether to check the codebase with *Pyright*.
    rstlint
        Whether to lint various *restructuredText* files with *rst-lint*.
    """

    if pyright:
        message_box('Checking codebase with "Pyright"...')
        ctx.run("pyright --threads --skipunannotated --level warning")

    if rstlint:
        message_box('Linting "README.rst" file...')
        ctx.run("rst-lint README.rst")


@task
def precommit(ctx: Context) -> None:
    """
    Run the "pre-commit" hooks on the codebase.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Running "pre-commit" hooks on the codebase...')
    ctx.run("pre-commit run --all-files")


@task
def tests(ctx: Context) -> None:
    """
    Run the unit tests with *Pytest*.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Running "Pytest"...')
    ctx.run(
        "pytest "
        "--doctest-modules "
        f"--ignore={PYTHON_PACKAGE_NAME}/examples "
        f"--cov={PYTHON_PACKAGE_NAME} "
        f"{PYTHON_PACKAGE_NAME}"
    )


@task
def examples(ctx: Context) -> None:
    """
    Run the examples.

    Parameters
    ----------
    ctx
        Context.
    plots
        Whether to skip or only run the plotting examples: This a mutually
        exclusive switch.
    """

    message_box("Running examples...")

    message_box(PYTHON_PACKAGE_NAME)

    for root, _dirnames, filenames in os.walk("examples"):
        for filename in fnmatch.filter(filenames, "*.py"):
            message_box(filename)
            ctx.run(f"python {os.path.join(root, filename)}")


@task(formatting, quality, precommit, tests, examples)
def preflight(ctx: Context) -> None:  # noqa: ARG001
    """
    Perform the preflight tasks.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Finishing "Preflight"...')


@task
def docs(
    ctx: Context,
    html: bool = True,
    pdf: bool = True,
) -> None:
    """
    Build the documentation.

    Parameters
    ----------
    ctx
        Context.
    plots
        Whether to generate the documentation plots.
    html
        Whether to build the *HTML* documentation.
    pdf
        Whether to build the *PDF* documentation.
    """
    with ctx.prefix("export COLOUR_SCIENCE__DOCUMENTATION_BUILD=True"), ctx.cd("docs"):
        if html:
            message_box('Building "HTML" documentation...')
            ctx.run("make html")

        if pdf:
            message_box('Building "PDF" documentation...')
            ctx.run("make latexpdf")


@task
def todo(ctx: Context) -> None:
    """
    Export the TODO items.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Exporting "TODO" items...')

    with ctx.cd("utilities"):
        ctx.run("./export_todo.py")


@task
def requirements(ctx: Context) -> None:
    """
    Export the *requirements.txt* file.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Exporting "requirements.txt" file...')
    ctx.run('uv export --no-hashes --all-extras | grep -v "-e \\." > requirements.txt')

    message_box('Exporting "docs/requirements.txt" file...')
    ctx.run(
        'uv export --no-hashes --all-extras --no-dev | grep -v "-e \\." > '
        "docs/requirements.txt"
    )


@task(clean, preflight, docs, todo, requirements)
def build(ctx: Context) -> None:
    """
    Build the project and runs dependency tasks.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box("Building...")
    ctx.run("uv build")
    ctx.run("twine check dist/*")


@task
def virtualise(ctx: Context, tests: bool = True) -> None:
    """
    Create a virtual environment for the project build.

    Parameters
    ----------
    ctx
        Context.
    tests
        Whether to run tests on the virtual environment.
    """

    unique_name = f"{PYPI_PACKAGE_NAME}-{uuid.uuid1()}"
    with ctx.cd("dist"):
        ctx.run(f"tar -xvf {PYPI_ARCHIVE_NAME}-{APPLICATION_VERSION}.tar.gz")
        ctx.run(f"mv {PYPI_ARCHIVE_NAME}-{APPLICATION_VERSION} {unique_name}")
        with ctx.cd(unique_name):
            ctx.run("uv sync --all-extras --no-dev")
            if tests:
                ctx.run(
                    "source .venv/bin/activate && "
                    "uv run pytest "
                    "--doctest-modules "
                    f"--ignore={PYTHON_PACKAGE_NAME}/examples "
                    f"{PYTHON_PACKAGE_NAME}",
                    env={"MPLBACKEND": "AGG"},
                )


@task
def tag(ctx: Context, remote_name: str = "upstream") -> None:
    """
    Tag the repository according to defined version using *git-flow*.

    Parameters
    ----------
    ctx
        Context.

    remote_name
        Name of the remote repository in the local git repository.
    """

    message_box("Tagging...")
    result = ctx.run("git rev-parse --abbrev-ref HEAD", hide="both")

    if result.stdout.strip() != "develop":  # pyright: ignore
        msg = "Are you still on a feature or master branch?"
        raise RuntimeError(msg)

    with open(os.path.join(PYTHON_PACKAGE_NAME, "__init__.py")) as file_handle:
        file_content = file_handle.read()
        major_version = re.search(
            '__major_version__\\s+=\\s+"(.*)"', file_content
        ).group(  # pyright: ignore
            1
        )
        minor_version = re.search(
            '__minor_version__\\s+=\\s+"(.*)"', file_content
        ).group(  # pyright: ignore
            1
        )
        change_version = re.search(
            '__change_version__\\s+=\\s+"(.*)"', file_content
        ).group(  # pyright: ignore
            1
        )

        version = f"{major_version}.{minor_version}.{change_version}"

        result = ctx.run(f"git ls-remote --tags {remote_name}", hide="both")
        remote_tags = result.stdout.strip().split("\n")  # pyright: ignore
        tags = set()
        for remote_tag in remote_tags:
            if remote_tag:
                tags.add(remote_tag.split("refs/tags/")[1].replace("refs/tags/", "^{}"))
        version_tags = sorted(tags)
        if f"v{version}" in version_tags:
            msg = (
                f'A "{PYTHON_PACKAGE_NAME}" "v{version}" tag already exists in '
                f"remote repository!"
            )
            raise RuntimeError(msg)

        ctx.run(f"git flow release start v{version}")
        ctx.run(f"git flow release finish v{version}")


@task(build)
def release(ctx: Context) -> None:
    """
    Release the project to *Pypi* with *Twine*.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box("Releasing...")
    with ctx.cd("dist"):
        ctx.run("twine upload *.tar.gz")
        ctx.run("twine upload *.whl")


@task
def sha256(ctx: Context) -> None:
    """
    Compute the project *Pypi* package *sha256* with *OpenSSL*.

    Parameters
    ----------
    ctx
        Context.
    """

    message_box('Computing "sha256"...')
    with ctx.cd("dist"):
        ctx.run(f"openssl sha256 {PYPI_ARCHIVE_NAME}-*.tar.gz")


@task
def generate_cxf3_code(ctx: Context, target: str) -> None:
    """
    Generate the code for reading/writing CxF files.

    The output source files will be generated in the `colour_cxf.cxf3` folder.

    Parameters
    ----------
    ctx
        Context.
    target
        Source file that contains the *CxF* XML schema.
    """
    ctx.run(
        f"xsdata generate "
        f"--package colour_cxf.cxf3 "
        f"--include-header "
        f"--structure-style clusters "
        f"--docstring-style NumPy "
        f"--postponed-annotations "
        f"--union-type "
        f"--wrapper-fields "
        f"--unnest-classes "
        f"--compound-fields "
        f"{target}"
    )
