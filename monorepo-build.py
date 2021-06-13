import os
from git import Git


def get_files():
    git = Git()
    tracked_files = git.ls_files().split('\n')
    untracked_unignored_files = git.ls_files('--exclude-standard', '--others').split('\n')
    return sorted(tracked_files + untracked_unignored_files)


def get_directories_to_build(files):
    return [os.path.dirname(f) for f in files if os.path.basename(f) == 'image-name']


def get_directory_dependencies(files, directory):
    # TODO: Get entire project tree
    return [f for f in files if os.path.commonpath([directory, f]) == directory]


if __name__ == '__main__':
    files = get_files()
    directories_to_build = get_directories_to_build(files)
    
    for directory in directories_to_build:
        print(get_directory_dependencies(files, directory))

