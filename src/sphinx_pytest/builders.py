"""Sphinx builders for pytest."""
from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.dummy import DummyBuilder


class DoctreeBuilder(DummyBuilder):
    """A builder that only builds the the initial doctrees, without post-transforms.

    The doctrees are stored in the `doctrees` attribute, rather than be saved to disk.
    """

    name = "doctree"

    def init(self) -> None:
        self.doctrees: dict[str, nodes.document] = {}

    def write_doctree(self, docname: str, doctree: nodes.document) -> None:
        # save the doctree instead of pickling to disk
        self.doctrees[docname] = doctree

    def write(self, *args, **kwargs) -> None:
        # don't apply post-transforms
        pass


def setup(app: Sphinx) -> dict:
    app.add_builder(DoctreeBuilder)
    return {
        "version": "1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
