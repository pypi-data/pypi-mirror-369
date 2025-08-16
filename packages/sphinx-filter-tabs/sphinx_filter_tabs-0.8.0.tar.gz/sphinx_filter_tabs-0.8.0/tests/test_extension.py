import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp
from sphinx.errors import SphinxError

# A standard RST content fixture for tests
@pytest.fixture()
def test_rst_content():
    return """
A Test Document
===============

.. filter-tabs:: Python, Rust (default), Go

    .. tab:: General

        This is general content.

    .. tab:: Python

        This is Python content.

    .. tab:: Rust

        This is Rust content.
"""

@pytest.mark.sphinx('html')
def test_html_structure_and_styles(app: SphinxTestApp, test_rst_content):
    """Checks the generated HTML structure and inline CSS variables."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()

    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert container, "Main container .sft-container not found"

    # Test that the inline style attribute exists
    assert container.has_attr('style'), "Container is missing the style attribute"
    assert "--sft-border-radius: 8px" in container['style']

@pytest.mark.sphinx('html', confoverrides={'filter_tabs_border_radius': '20px'})
def test_config_overrides_work(app: SphinxTestApp, test_rst_content):
    """Ensures that conf.py overrides are reflected in the style attribute."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    assert container.has_attr('style'), "Container is missing the style attribute"
    assert "--sft-border-radius: 20px" in container['style']

@pytest.mark.sphinx('latex')
def test_latex_fallback_renders_admonitions(app: SphinxTestApp, test_rst_content):
    """Checks that the LaTeX builder creates simple admonitions as a fallback."""
    app.srcdir.joinpath('index.rst').write_text(test_rst_content)
    app.build()
    
    # Look for the correct TeX filename based on the test project's name
    result = (app.outdir / 'sphinxtestproject.tex').read_text()

    # General content should appear directly
    assert 'This is general content.' in result
    assert r'\begin{sphinxadmonition}{note}{General}' not in result

    # Specific tabs should be titled admonitions
    assert r'\begin{sphinxadmonition}{note}{Python}' in result
    assert 'This is Python content.' in result
    assert r'\begin{sphinxadmonition}{note}{Rust}' in result
    assert 'This is Rust content.' in result

@pytest.mark.sphinx('html')
def test_error_on_orphan_tab(app: SphinxTestApp, status, warning):
    """Tests that a `tab` directive outside `filter-tabs` logs an error."""
    app.srcdir.joinpath('index.rst').write_text(".. tab:: Orphan")
    app.build()

    # Check for the error message in the warning stream instead of expecting a crash.
    warnings = warning.getvalue()
    assert "`tab` can only be used inside a `filter-tabs` directive" in warnings
