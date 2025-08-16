# Configuration file for the Sphinx documentation builder.
import importlib
import inspect
import os


# -- Project information -----------------------------------------------------

project = "AGOX"
copyright = "2022-2025, AGOX Contributors"
author = "Mads-Peter V. C"

# from agox.__version__ import __version__ as agox_version
# The full version, including alpha/beta/rc tags
# Version Number:
import re
from agox import __version__

release = __version__

# -- Prolog ------------------------------------------------------------------

rst_prolog = """
.. |CHGNet| replace:: Can easily run with CHGNet using the calculator provided by the chgnet package (``pip install chgnet``). See https://chgnet.lbl.gov/ for more info.
.. |EMT| replace:: EMT is a quick potential that is bundled with ASE, not accurate enough for material science, but useful testing search algorithms.
.. |GPAW| replace:: Tested with GPAW 23.9.1 and ASE 3.25.0. See https://wiki.fysik.dtu.dk/gpaw/ for more info.
.. |ORCA| replace:: Tested with ORCA 5.0.4 and ASE 3.23.0, see https://wiki.fysik.dtu.dk/ase/ase/calculators/orca.html and https://sites.google.com/site/orcainputlibrary for more info.
.. |VASP| replace:: Tested with VASP 5.4.4 and ASE 3.23.0, see https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.html for more information. As of Feb 2025 VASP calculations done with ASE do not raise an exception when not the SCF does not converge, to avoid adding unphysical structures to the database the callback function described here :ref:`EVAL_CALLBACK` is used. 
"""

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.duration",
    "sphinx_tabs.tabs",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "sphinx.ext.linkcode",
    # 'sphinx.ext.autosectionlabel',
    # 'sphinx.ext.graphviz',
    # 'sphinx.ext.inheritance_diagram',
    "sphinx.ext.doctest",
    "sphinx_copybutton",
    "sphinx_design",
]

# Document Python Code
autoapi_type = "python"
autoapi_dirs = ["../../agox/"]
autoapi_ignore = ["*/*test*"]
autodoc_typehints = "description"
autoapi_keep_files = False
autoapi_options = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_add_toctree_entry = False

autoapi_template_dir = "../autoapi_templates"

# Limk code:
code_url = "https://gitlab.com/agox/agox/-/blob/dev/{}?ref_type=heads#L{}-L{}"


def linkcode_resolve(domain, info):
    # Non-linkable objects from the starter kit in the tutorial.
    if domain == "js" or info["module"] == "connect4":
        return

    assert domain == "py", "expected only Python objects"

    try:
        mod = importlib.import_module(info["module"])
        if "." in info["fullname"]:
            objname, attrname = info["fullname"].split(".")
            obj = getattr(mod, objname)
            try:
                # object is a method of a class
                obj = getattr(obj, attrname)
            except AttributeError:
                # object is an attribute of a class
                return None
        else:
            obj = getattr(mod, info["fullname"])

        try:
            file = inspect.getsourcefile(obj)
            lines = inspect.getsourcelines(obj)
        except TypeError:
            # e.g. object is a typing.Union
            return None
        except OSError:  # Cytohn
            return None
        except:  # other issues
            return None

        file = os.path.relpath(file, os.path.abspath(".."))

        start, end = lines[1], lines[1] + len(lines[0]) - 1

        return code_url.format(file, start, end)
    except:  # The mother of catching all exceptions
        return None


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_favicon = "A.ico"

sd_custom_directives = {
    'script-tab-set': {
        'inherit': 'tab-set',
        'options':
            {
                "class": "sd-pl-1 sd-ml-3 sd-rounded-2"
            }
    }
}
