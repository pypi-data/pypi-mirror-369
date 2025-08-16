import functools
from typing import List

# from agox import __version__

ICON = """
       _            _  _  _        _  _  _  _    _           _ 
     _(_)_       _ (_)(_)(_) _   _(_)(_)(_)(_)_ (_)_       _(_)
   _(_) (_)_    (_)         (_) (_)          (_)  (_)_   _(_)  
 _(_)     (_)_  (_)    _  _  _  (_)          (_)    (_)_(_)    
(_) _  _  _ (_) (_)   (_)(_)(_) (_)          (_)     _(_)_     
(_)(_)(_)(_)(_) (_)         (_) (_)          (_)   _(_) (_)_   
(_)         (_) (_) _  _  _ (_) (_)_  _  _  _(_) _(_)     (_)_ 
(_)         (_)    (_)(_)(_)(_)   (_)(_)(_)(_)  (_)         (_)  v{}_{} \n
"""


def get_git_revision_short_hash() -> str:
    import os
    import subprocess

    import agox

    try:
        dir_path = os.path.dirname(agox.__path__[0])
        version_string = (
            subprocess.check_output(["git", f"--git-dir={dir_path}/.git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        version_string = "unknown"
    except BlockingIOError:
        version_string = "unknown"
    except FileNotFoundError:
        version_string = "unknown"

    return version_string


LINE_LENGTH = 79
PADDING_CHARACTER = "="
TERMINATE_CHARACTER = "|"


def get_icon():
    # version_string = get_git_revision_short_hash()
    return ICON