import os
from pathlib import Path


class FileSystem:
    def __init__(
        self, root_path: str, scan_folder: str = None, destination_folder: str = None
    ):
        self._root_path = root_path
        self._scan_folder = scan_folder
        self._destination_folder = destination_folder
        self._destination_path = self._destination_path()
        self._media_extensions = self._get_media_extensions()
        self._excluded_dirs = self._get_excluded_dirs()
        self._scan_media_files = []
        self._scan_dir = self.get_scan_dir()
        self._file_mover = FileMover(root_path)

    def _destination_path(self):
        if self._destination_folder:
            return os.path.join(self._root_path, self._destination_folder)

        if self._scan_folder:
            return os.path.join(self._root_path, self._scan_folder)

        return self._root_path

    def _get_media_extensions(self):
        extensions = os.environ.get("MEDIA_EXTENSIONS")
        if not extensions:
            raise ValueError("MEDIA_EXTENSIONS is not set")
        return extensions.split(",")

    def _get_excluded_dirs(self):
        exclude_folders = os.environ.get("EXCLUDE_FOLDERS")
        exclude_folders = exclude_folders.split(",") if exclude_folders else []
        return [os.path.join(self._root_path, folder) for folder in exclude_folders]

    def _is_file_excluded(self, file_path: str) -> bool:
        extension = os.path.splitext(file_path)[1]
        if extension not in self._media_extensions:
            return True

        for excluded_dir in self._excluded_dirs:
            if file_path.startswith(excluded_dir):
                return True

        return False

    def get_scan_dir(self):
        if not self._scan_folder:
            return self._root_path

        return os.path.join(self._root_path, self._scan_folder)

    def get_encode_temp_path(self, original_path: str):
        temp_folder = os.environ.get("TEMP_FOLDER")
        if not temp_folder:
            raise ValueError("TEMP_FOLDER is not set")

        dest_dir = os.path.join(self._root_path, temp_folder, "encodes")
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        original_file_name = os.path.basename(original_path)
        temp_path = os.path.join(dest_dir, original_file_name)

        return temp_path

    def scan_dir_files(self) -> list:
        for dirpath, _, filenames in os.walk(self._scan_dir):
            for filename in filenames:
                original_path = os.path.join(dirpath, filename)
                if self._is_file_excluded(original_path):
                    continue

                self._scan_media_files.append(original_path)

        return self._scan_media_files

    def file_exist(self, path: str) -> bool:
        return os.path.isfile(path)

    def get_destination_path(self, relative_path: str):
        return os.path.join(self._destination_path, relative_path)

    def move_original_to_temp(self, original_path: str) -> str:
        return self._file_mover.move_original_to_temp(original_path)

    def move(self, original_path: str, dest_path: str):
        self._file_mover.move(original_path, dest_path)


class FileMover:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def _create_directory_if_not_exists(self, path: str):
        """Create directory if it doesn't already exist"""
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_temp_folder_path(self):
        """Get the path to the temporary folder"""
        temp_folder = os.environ.get("TEMP_FOLDER")
        if not temp_folder:
            raise ValueError("TEMP_FOLDER is not set")
        return os.path.join(self.root_path, temp_folder)

    def _get_originals_folder_path(self):
        """Get the path to the originals folder within the temporary folder"""
        return os.path.join(self._get_temp_folder_path(), "originals")

    def _move_file(self, original_path: str, dest_path: str):
        """Move file from original path to destination path"""
        if original_path == dest_path:
            return
        os.rename(original_path, dest_path)

    def move(self, original_path: str, dest_path: str):
        """Move file from original path to destination path"""
        self._create_directory_if_not_exists(os.path.dirname(dest_path))
        self._move_file(original_path, dest_path)

    def move_to_temp(self, original_path: str):
        """Move file to temporary folder"""
        temp_folder_path = self._get_temp_folder_path()
        self._create_directory_if_not_exists(temp_folder_path)
        original_file_name = Path(original_path).name
        temp_path = os.path.join(temp_folder_path, original_file_name)
        self._move_file(original_path, temp_path)

        return temp_path

    def move_original_to_temp(self, original_path: str):
        """Move original file to originals folder within the temporary folder"""
        originals_folder_path = self._get_originals_folder_path()
        self._create_directory_if_not_exists(originals_folder_path)
        original_file_name = Path(original_path).name
        temp_path = os.path.join(originals_folder_path, original_file_name)
        self._move_file(original_path, temp_path)

        return temp_path
