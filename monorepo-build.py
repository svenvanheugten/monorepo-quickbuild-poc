import os
import hashlib
from filehash import FileHash
from git import Git


filehasher = FileHash()


class File:
    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.__hash = None

    @property
    def hash(self):
        if self.__hash is None:
            self.__hash = filehasher.hash_file(self.filename)
        return self.__hash

    def in_directory(self, directory):
        return os.path.commonpath([directory, self.filename]) == directory

    def __repr__(self):
        return self.filename


def get_files():
    git = Git()
    tracked_files = git.ls_files().split('\n')
    untracked_unignored_files = git.ls_files('--exclude-standard', '--others').split('\n')
    filenames = tracked_files + untracked_unignored_files
    return [File(f) for f in filenames]


def get_directories_to_build(files):
    return [f.dirname for f in files if f.basename == 'image-name']


def get_directory_dependencies(files, directory):
    # TODO: Get entire project tree
    # TODO: Possibly prepare a structure that allows this to be done faster than iterating over all files
    return [f for f in files if f.in_directory(directory)]


def get_combined_hash(files):
    return hashlib.sha256(','.join(f.filename + ':' + f.hash for f in files).encode('utf-8')).hexdigest()


if __name__ == '__main__':
    files = get_files()
    directories_to_build = get_directories_to_build(files)

    for directory in directories_to_build:
        print(get_combined_hash(get_directory_dependencies(files, directory)))

