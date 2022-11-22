# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = "Jacques"
copyright = "2022, Egor Svezhintsev"
author = "Egor Svezhintsev"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

devdir = ""
try:
    if os.environ["DEVDIR"]:
        devdir = os.environ["DEVDIR"]
except KeyError:
    print("Unable to obtain $DEVDIR from the environment")

sys.path.insert(
    0,
    devdir
    + "/../jacques-vsc/PythonInterpreter/Mac/install/lib/python3.10/site-packages",
)
sys.path.insert(0, devdir + "/src")

extensions = ["sphinx.ext.autodoc", "sphinx.ext.githubpages"]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".pytest_cache",
    "**tests**",
    "*.egg-info",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

master_doc = "modules"
html_theme = "alabaster"
html_static_path = ["_static"]
