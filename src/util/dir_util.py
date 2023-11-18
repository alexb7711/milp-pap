"""
This file provides utility for checking and creating directories.
"""

# System Modules
import os

##==============================================================================
#
def dir_exists(path: str) -> bool:
    """
    Checks to see if a directory exists.

    Input:
      * path: Path to the directory

    Output:
      * bool: True if directory exists, false if not
    """
    return os.path.isdir(path)

##==============================================================================
#
def create_dir(path: str) -> None:
    """
    Checks to see if the specified directory exists, if it does not the directory
    is created.

    Input:
      - path: Path to the directory

    Output:
      - None
    """
    if not dir_exists(path):
        os.makedirs(path)
        print("Created :", path)
    return
