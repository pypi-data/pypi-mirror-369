"""
Type stubs for puremagic package.
"""

import os

class PureError(LookupError):
    """Do not have that type of file in our databanks."""
    ...

def from_string(
    string: str | bytes, 
    mime: bool = False, 
    filename: os.PathLike[str] | str | None = None
) -> str:
    """Detect file type from string content."""
    ...