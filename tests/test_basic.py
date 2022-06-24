def test_basic(sphinx_doctree):
    result = sphinx_doctree("abc")
    assert (
        result.pformat()
        == '<document source="<src>/index.rst">\n    <paragraph>\n        abc'
    )


def test_no_transforms(sphinx_doctree_no_tr):
    """Return the doctree, before any transforms have been applied."""
    result = sphinx_doctree_no_tr(".. _target:\n\nheader\n------\n")
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


def test_html_builder(sphinx_doctree):
    sphinx_doctree.buildername = "html"
    result = sphinx_doctree(".. only:: html\n\n   abc\n\n.. only:: latex\n\n   xyz\n")
    assert (
        result.get_resolved_pformat()
        == '<document source="<src>/index.rst">\n    <paragraph>\n        abc'
        '\n    <comment xml:space="preserve">'
    )
