"""Damage and Loss Model Library Sphinx configuration."""

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path('./_extensions').resolve()))

# -- Project information -----------------------------------------------------
project = 'Damage and Loss Model Library'
copyright = (  # noqa: A001
    f'{datetime.now().year}, Leland Stanford Junior '  # noqa: DTZ005
    f'University and The Regents of the University of California'
)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'numpydoc',
    'sphinx_design',
    'sphinxcontrib.bibtex',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx_generate_dl_doc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = ['css/custom.css']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Extension configuration

autosummary_generate = True  # Turn on sphinx.ext.autosummary

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/objects.inv', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/objects.inv', None),
}

numpydoc_show_class_members = False  # TODO(JVM): remove and extend docstrings

nbsphinx_custom_formats = {
    '.pct.py': ['jupytext.reads', {'fmt': 'py:percent'}],
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'analytics_id': None,  # TODO (AZ): Add analytics ID.
    'logo_only': True,
    'collapse_navigation': False,
    'prev_next_buttons_location': None,
    'navigation_depth': 8,
    'style_nav_header_background': '#F2F2F2',
}
html_show_sphinx = False  # Removes "Built with Sphinx using a theme [...]"
html_show_sourcelink = (
    False  # Remove 'view source code' from top of page (for html, not python)
)
numfig = True
bibtex_bibfiles = ['references.bib']
bibtex_style = 'plain'
