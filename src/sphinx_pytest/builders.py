"""Sphinx builders for pytest."""

from __future__ import annotations

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.dummy import DummyBuilder


class DoctreeBuilder(DummyBuilder):
    """A builder that only builds the the initial doctrees,
    without subsequent events or post-transforms.

    The doctrees are stored in the `doctrees` attribute, rather than saved to disk.
    """

    name = "doctree"

    def init(self) -> None:
        self.doctrees: dict[str, nodes.document] = {}

    def write_doctree(
        self, docname: str, doctree: nodes.document, *, _cache: bool = True
    ) -> None:
        # save the doctree instead of pickling to disk
        self.doctrees[docname] = doctree

    def build(self, *args, **kwargs) -> None:
        # don't run anything after the initial doctree reads
        self.read()


def setup(app: Sphinx) -> dict:
    app.add_builder(DoctreeBuilder)
    return {
        "version": "1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
