import os
from filehash import FileHash
from git import Git


filehasher = FileHash()


class File:
    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.hash = filehasher.hash_file(filename)
    
    def in_directory(self, directory):
        return os.path.commonpath([directory, self.filename]) == directory

    def __repr__(self):
        return self.filename


def get_files():
    git = Git()
    tracked_files = git.ls_files().split('\n')
    untracked_unignored_files = git.ls_files('--exclude-standard', '--others').split('\n')
    filenames = tracked_files + untracked_unignored_files
    files = [File(f) for f in filenames]
    return sorted(files, key=lambda f: f.filename)


def get_directories_to_build(files):
    return [f.dirname for f in files if f.basename == 'image-name']


def get_directory_dependencies(files, directory):
    # TODO: Get entire project tree
    return [f for f in files if f.in_directory(directory)]


if __name__ == '__main__':
    files = get_files()
    directories_to_build = get_directories_to_build(files)

    for directory in directories_to_build:
        print(get_directory_dependencies(files, directory))

