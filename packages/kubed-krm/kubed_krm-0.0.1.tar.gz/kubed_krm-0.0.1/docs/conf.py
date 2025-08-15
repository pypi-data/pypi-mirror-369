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
sys.path.insert(0, os.path.abspath('../lib'))
from kubed.krm import common as c, files as f
import sphinx_theme
from sphinx_gallery.sorting import FileNameSortKey

# -- Project information -----------------------------------------------------

project = 'kubed-krm-docs'
copyright = '2022, Kelly Ferrone'
author = 'Kelly Ferrone'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    # 'sphinx_gallery.gen_gallery',
    # 'sphinx.ext.intersphinx',
    'myst_parser',
    'sphinx_jinja',
    'sphinx_rtd_theme',
    'sphinx_panels',
    'sphinx_copybutton',
    'sphinx-jsonschema'
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
html_theme = 'stanford_theme'
html_theme_path = [sphinx_theme.get_html_theme_path('stanford-theme')]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# sphinx-gallery configuration
# sphinx_gallery_conf = {
#     # path to your example scripts
#     'examples_dirs': [],
#     # path to where to save gallery generated output
#     'gallery_dirs': [],
#     # specify that examples should be ordered according to filename
#     'within_subsection_order': FileNameSortKey,
#     # directory where function granular galleries are stored
#     'backreferences_dir': 'gen_modules/backreferences',
#     # Modules for which function level galleries are created.  In
#     # this case sphinx_gallery and numpy in a tuple of strings.
#     'doc_module': ('SampleModule'),
# }

# configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {}

myst_enable_extensions = [
  "colon_fence",
  "deflist",
  "linkify",
  "substitution"
]


jinja_contexts = {
    'replicate': f.load_yaml('../examples/replicate/kustomization.yaml')
}
