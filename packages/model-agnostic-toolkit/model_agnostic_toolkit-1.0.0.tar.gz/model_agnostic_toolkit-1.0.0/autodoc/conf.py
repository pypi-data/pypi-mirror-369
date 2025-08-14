# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ModelAgnosticToolkit"
copyright = "2025, Chair for Intelligence in Quality Sensing | RWTH Aachen University"
author = "Tobias Schulze"

import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx.ext.autosummary',
    'myst_parser',
    'sphinxcontrib.mermaid',
    'sphinx.ext.autosectionlabel'
]

markdown_anchor_sections = True
markdown_anchor_signatures = True
markdown_uri_doc_suffix = ".md"

# Napoleon settings
napoleon_google_docstring = True
#napoleon_numpy_docstring = True
#napoleon_include_init_with_doc = False
#napoleon_include_private_with_doc = False
#napoleon_include_special_with_doc = False
#napoleon_use_admonition_for_examples = True
#napoleon_use_admonition_for_notes = True
#napoleon_use_admonition_for_references = True
#napoleon_use_ivar = True
#napoleon_use_param = True
#napoleon_use_rtype = True
#napoleon_use_keyword = True
#napoleon_custom_sections = None

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Autodoc settings
autoclass_content = 'both'

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

