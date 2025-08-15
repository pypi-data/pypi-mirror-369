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
import datetime
import importlib.metadata
import os
import re
import sys

project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
src_dir = os.path.join(project_dir, 'src')
sys.path.insert(0, src_dir)


# -- Project information -----------------------------------------------------

package_name = 'momotor-engine-options'
project = 'Momotor Engine Options'
copyright = '2021-%d, Eindhoven University of Technology' % datetime.datetime.now().year
author = 'E.T.J. Scheffers'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = importlib.metadata.version(package_name)
# The short X.Y version.
version = re.match(r'\d+\.\d+', release).group(0)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'momotor.options.sphinx.option',
    'momotor.options.sphinx.fixextref',  # Must be listed after intersphinx
    'pytest_doctestplus.sphinx.doctestplus',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

rst_epilog = """
.. _Momotor Engine: https://momotor.org/

.. role:: xml(code)
   :language: xml
"""

# -- Options for autodoc -----------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Options for intersphinx -------------------------------------------------


def inventory(domain, name):
    # Try to collect intersphinx mapping from development environment first, then from online version
    try:
        local_docs = os.path.join(os.environ.get('LOCAL_DOCS_PATH', 'docs'), name)
        local_docs = os.path.realpath(local_docs)
    except FileNotFoundError:
        pass
    else:
        local_inv = os.path.join(local_docs, 'objects.inv')
        if os.path.exists(local_inv):
            base_url = os.environ.get('LOCAL_DOCS_BASE_URL')
            if base_url and '://' not in base_url and not base_url.startswith('/'):
                base_url = '/'+base_url
            return f'{base_url}/docs/build/{name}', local_inv

    if 'rc' in release:
        # Since this package is a dev release, use dev releases for intersphinx too
        return f'https://momotor.org/doc/{domain}/{name}/dev/latest', None

    return f'https://momotor.org/doc/{domain}/{name}', None


intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'momotor-bundles': inventory('engine', 'momotor-bundles'),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_copy_source = False

html_theme_options = {
    "light_logo": "logo-text.png",
    "dark_logo": "logo-text-negative.png",
}

html_context = {
    'project_url': 'https://momotor.org/',
    'pypi_url': f'https://pypi.org/project/{package_name}/',
    'repository_url': f'https://gitlab.tue.nl/momotor/engine-py3/{package_name}/',
}

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
        "projectlinks.html",
    ]
}

# -- Options for LaTeX output ---------------------------------------------------

_PREAMBLE = r"""
\DeclareUnicodeCharacter{2794}{$\rightarrow$}
"""

latex_elements = {
    'preamble': _PREAMBLE,
}
