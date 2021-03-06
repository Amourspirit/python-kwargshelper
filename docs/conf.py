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
from docutils.parsers.rst import Directive
from docutils import nodes, statemachine
from os.path import basename
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
sys.path.insert(0, os.path.abspath('..'))

from kwhelp import __version__

# -- Project information -----------------------------------------------------

project = 'kwargshelper'
copyright = '2021, :Barry-Thomas-Paul: Moss'
author = ':Barry-Thomas-Paul: Moss'

# The full version, including alpha/beta/rc tags
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = []

if html_theme == 'sphinx_rtd_theme':
    html_css_files.append('css/readthedocs_custom.css')

# Napoleon settings
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# https://stackoverflow.com/questions/7250659/how-to-use-python-to-programmatically-generate-part-of-sphinx-documentation/18143318#18143318
# https://stackoverflow.com/questions/27875455/displaying-dictionary-data-in-sphinx-documentation
# custom directive

autodoc_default_options = {
    'member-order': 'groupwise'
}

class ExecDirective(Directive):
    """Execute the specified python code and insert the output into the document"""
    has_content = True

    def run(self):
        oldStdout, sys.stdout = sys.stdout, StringIO()

        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)

        try:
            exec('\n'.join(self.content))
            text = sys.stdout.getvalue()
            lines = statemachine.string2lines(
                text, tab_width, convert_whitespace=True)
            self.state_machine.insert_input(lines, source)
            return []
        except Exception:
            return [nodes.error(None, nodes.paragraph(text="Unable to execute python code at %s:%d:" % (basename(source), self.lineno)), nodes.paragraph(text=str(sys.exc_info()[1])))]
        finally:
            sys.stdout = oldStdout


def setup(app):
    app.add_directive('exec', ExecDirective)
