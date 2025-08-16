import os
from pathlib import Path

class LibUtils:
    """
    Library utilities
    """

    @classmethod
    def get_lib_home(cls):
        """
        it returns the path to the library home
        :return:
        """

        root_folder = Path(os.getenv("LGO_HOME", Path.cwd()))
        lib_home = root_folder / ".lgopy"
        return lib_home


