## pip install sphinx sphinx_rtd_theme numpydoc

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

import befordata

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "BeForData"
copyright = "2024, Oliver Lindemann"
author = "Oliver Lindemann"
release = befordata.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    # "sphinx.ext.napoleon",
    "numpydoc",
    "myst_parser",  # markdown support
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = [".rst", ".md"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
# html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_show_sourcelink = False
html_theme_options = {"show_nav_level": 2, "show_toc_level": 3}

numpydoc_show_class_members = True
add_module_names = False


typehints_use_rtype = False
typehints_use_signature = False
typehints_use_signature_return = False

autodoc_type_aliases = {
    "NDArray": "NDArray",
    "DataFrame": "pd.DataFrame",
    "ArrayLike": "ArrayLike",
}
