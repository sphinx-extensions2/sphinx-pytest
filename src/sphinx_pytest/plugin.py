"""The pytest plugin."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.core import Publisher
import pytest
from sphinx.environment import BuildEnvironment
from sphinx.testing.path import path
from sphinx.testing.util import SphinxTestApp

from .builders import DoctreeBuilder

pytest_plugins = ("sphinx.testing.fixtures",)


@pytest.fixture
def sphinx_doctree(make_app: type[SphinxTestApp], tmp_path: Path):
    """Create a sphinx doctree (before post-transforms)."""
    yield CreateDoctree(app_cls=make_app, srcdir=tmp_path / "src")


@pytest.fixture
def sphinx_doctree_no_tr(make_app: type[SphinxTestApp], tmp_path: Path, monkeypatch):
    """Create a sphinx doctree with no transforms."""

    def _apply_transforms(self):
        pass

    monkeypatch.setattr(Publisher, "apply_transforms", _apply_transforms)
    yield CreateDoctree(app_cls=make_app, srcdir=tmp_path / "src")


class AppWrapper:
    """Wrapper for SphinxTestApp to make it easier to use."""

    def __init__(self, app: SphinxTestApp) -> None:
        self._app = app

    @property
    def app(self) -> SphinxTestApp:
        return self._app

    @property
    def env(self) -> BuildEnvironment:
        assert self._app.env is not None
        return self._app.env

    @property
    def builder(self) -> DoctreeBuilder:
        return self._app.builder  # type: ignore

    def build(self) -> AppWrapper:
        self._app.build()
        return self

    @property
    def warnings(self) -> str:
        text = self._app._warning.getvalue()
        return text.replace(str(self._app.srcdir), "<src>")

    @property
    def doctrees(self) -> dict[str, nodes.document]:
        """The built doctrees (before post-transforms)."""
        return self.builder.doctrees

    def pformat(self, docname: str = "index") -> str:
        """Return an indented pseudo-XML representation.

        The src directory is replaced with <src>, for reproducibility.
        """
        text = self.doctrees[docname].pformat()
        return text.replace(str(self._app.srcdir) + os.sep, "<src>/").rstrip()

    def get_resolved_doctree(self, docname: str = "index") -> nodes.document:
        """Return the doctree after post-transforms.

        Note only builder agnostic post-transforms will be applied, e.g. not ones for 'html' etc.
        """
        doctree = self.doctrees[docname].deepcopy()
        self.env.apply_post_transforms(doctree, docname)
        # note, this does not resolve toctrees, as in:
        # https://github.com/sphinx-doc/sphinx/blob/05a898ecb4ff8e654a053a1ba5131715a4514812/sphinx/environment/__init__.py#L538
        return doctree


class CreateDoctree:
    def __init__(self, app_cls: type[SphinxTestApp], srcdir: Path) -> None:
        self._app_cls = app_cls
        self.srcdir = srcdir
        self.srcdir.mkdir(parents=True, exist_ok=True)
        # the test app always sets `confdir = srcdir`, as opposed to None,
        # which means a conf.py is required
        self.srcdir.joinpath("conf.py").write_text("", encoding="utf8")
        self.buildername = "doctree"
        self._confoverrides: dict[str, Any] = {}

    def set_conf(self, conf: dict[str, Any]) -> CreateDoctree:
        self._confoverrides = conf
        return self

    def __call__(
        self,
        content: str,
        filename: str = "index.rst",
        **kwargs,
    ) -> AppWrapper:
        """Create doctrees for a set of files."""

        self.srcdir.joinpath(filename).parent.mkdir(parents=True, exist_ok=True)
        self.srcdir.joinpath(filename).write_text(content, encoding="utf8")

        return AppWrapper(
            self._app_cls(
                srcdir=path(str(self.srcdir)),
                buildername=self.buildername,
                confoverrides=self._confoverrides,
                **kwargs,
            )
        ).build()
