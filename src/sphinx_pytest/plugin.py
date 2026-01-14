"""The pytest plugin."""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest
from docutils import nodes
from docutils.core import Publisher
from sphinx import version_info as sphinx_version_info
from sphinx.environment import BuildEnvironment
from sphinx.testing.util import SphinxTestApp
from sphinx.transforms import SphinxTransformer

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
    # in sphinx >= 9.0.0 SphinxTransformer is used
    monkeypatch.setattr(SphinxTransformer, "apply_transforms", _apply_transforms)
    yield CreateDoctree(app_cls=make_app, srcdir=tmp_path / "src")


class Doctrees(Mapping):
    """A mapping of doctree names to doctrees."""

    def __init__(self, env: BuildEnvironment):
        self._env = env

    def __getitem__(self, key: str) -> nodes.document:
        try:
            return self._env.get_doctree(key)
        except FileNotFoundError as err:
            raise KeyError(key) from err

    def __iter__(self) -> Iterator[str]:
        return iter(self._env.found_docs)

    def __len__(self) -> int:
        return len(self._env.found_docs)


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
        return self._app.builder  # type: ignore[return-value]

    def build(self) -> AppWrapper:
        self._app.build()
        return self

    @property
    def warnings(self) -> str:
        text = self._app._warning.getvalue()  # type: ignore[attr-defined]
        return text.replace(str(self._app.srcdir), "<src>")

    @property
    def doctrees(self) -> dict[str, nodes.document] | Doctrees:
        """The built doctrees (before post-transforms)."""
        try:
            return self.builder.doctrees
        except AttributeError:
            return Doctrees(self.env)

    def pformat(
        self, docname: str = "index", pop_doc_attrs=("translation_progress",)
    ) -> str:
        """Return an indented pseudo-XML representation.

        The src directory is replaced with <src>, for reproducibility.

        :param pop_doc_attrs: Remove these attributes of the doctree node,
            before converting to text.
            By default, ``translation_progress`` is removed for compatibility
            (added in sphinx 7.1).
        """
        doctree = self.doctrees[docname].deepcopy()
        for attr_name in pop_doc_attrs:
            doctree.attributes.pop(attr_name, None)
        text = doctree.pformat()
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

    def get_resolved_pformat(
        self, docname: str = "index", pop_doc_attrs=("translation_progress",)
    ) -> str:
        """Return an indented pseudo-XML representation, after post-transforms.

        The src directory is replaced with <src>, for reproducibility.

        :param pop_doc_attrs: Remove these attributes of the doctree node,
            before converting to text.
            By default, ``translation_progress`` is removed for compatibility
            (added in sphinx 7.1).
        """
        doctree = self.get_resolved_doctree(docname)
        for attr_name in pop_doc_attrs:
            doctree.attributes.pop(attr_name, None)
        text = doctree.pformat()
        return text.replace(str(self._app.srcdir) + os.sep, "<src>/").rstrip()


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

        srcdir: Any
        if sphinx_version_info >= (7, 2):
            srcdir = self.srcdir
        else:
            from sphinx.testing.path import path

            srcdir = path(str(self.srcdir))

        return AppWrapper(
            self._app_cls(
                srcdir=srcdir,
                buildername=self.buildername,
                confoverrides=self._confoverrides,
                **kwargs,
            )
        ).build()
