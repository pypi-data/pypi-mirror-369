import shutil
from pathlib import Path


class FileUtils:
    @staticmethod
    def clear_folder_contents(folder_path: Path):
        """
        Recursively deletes all files and subdirectories inside the given folder.
        The folder itself is not deleted.

        Args:
            folder_path (Path): The target folder to clear.
        """
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"{folder_path} is not a valid directory")

        for item in folder_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
