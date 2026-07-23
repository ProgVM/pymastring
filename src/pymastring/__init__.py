# Standard internal python structure for package initialization
from .core import patch_strings, MathJSONEncoder, MathChar

# Automatically apply forbiddenfruit patches on package import
patch_strings()

__all__ = ["MathJSONEncoder", "MathChar"]

