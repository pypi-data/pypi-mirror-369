import sys
if sys.platform.startswith("win"):
    from .omnicon_genericddsengine_py import *
else:
    from ._omnicon_genericddsengine_py import *
