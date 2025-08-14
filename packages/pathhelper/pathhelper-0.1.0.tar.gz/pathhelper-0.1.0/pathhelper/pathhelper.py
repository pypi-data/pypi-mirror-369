import os
import shutil
from abc import ABC, abstractmethod

# Abstract base class for path tools
class PathHelper(ABC):

    def __init__(self, path):
        self.path = os.path.abspath(path)

    @abstractmethod
    def check_exists(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    def create_if_missing(self):
        if not self.check_exists():
            self.create()

    def remove_if_present(self):
        if self.check_exists():
            self.remove()

class FileHelper(PathHelper):

    def check_exists(self):
        return os.path.isfile(self.path)

    def create(self):
        file_dir = os.path.dirname(self.path)
        DirHelper(file_dir).create_if_missing()
        with open(self.path, 'w') as f:
            pass  # create empty file

    def remove(self):
        os.remove(self.path)

# Directory path tool
class DirHelper(PathHelper):

    def check_exists(self):
        return os.path.isdir(self.path)

    def create(self):
        os.makedirs(self.path, exist_ok=True)

    def remove(self):
        shutil.rmtree(self.path)

# Context manager to run code within a directory
class RunInDir:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.prev_wd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, type, value, traceback):
        os.chdir(self.prev_wd)

# Example usage
if __name__ == "__main__":
    temp_dir = 'temp'
    dir_helper = DirHelper(temp_dir)
    dir_helper.create_if_missing()

    print("Before:", os.getcwd())
    with RunInDir(temp_dir):
        print("Inside:", os.getcwd())
    print("After:", os.getcwd())

    dir_tool.remove_if_present()
