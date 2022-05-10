# sphinx-pytest

[![PyPI][pypi-badge]][pypi-link]

Helpful pytest fixtures for sphinx extensions.

Sphinx is annoying, because the modularity is not great,
meaning that there is no real way just to convert single documents in isolation, etc.

This extension mainly provides some pytest fixtures to "simulate" converting some source text to docutils AST at different stages; before transforms, after transforms, etc.


## Installation

```
pip install sphinx-pytest
```

## Examples

```python
from sphinx_pytest.plugin import CreateDoctree

def test_no_transforms(sphinx_doctree_no_tr: CreateDoctree):
    """Return the doctree, before any transforms have been applied."""
    result = sphinx_doctree_no_transforms(".. _target:\n\nheader\n------\n")
    assert (
        result.pformat()
        == """\
<document source="<src>/index.rst">
    <target ids="target" names="target">
    <section ids="header" names="header">
        <title>
            header
""".rstrip()
    )
```

```python
def test_with_transforms(sphinx_doctree):
    """Return the doctree, after transforms (but not post-transforms)."""
    result = sphinx_doctree(".. _target:\n\nheader\n------\n")
    assert (
        result.pformat()
        == """\
<document source="<src>/index.rst">
    <target refid="target">
    <section ids="header target" names="header target">
        <title>
            header
""".rstrip()
    )
```


[pypi-badge]: https://img.shields.io/pypi/v/sphinx_pytest.svg
[pypi-link]: https://pypi.org/project/sphinx_pytest
