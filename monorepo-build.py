import os
import sys
import docker
import hashlib
from filehash import FileHash
import git


filehasher = FileHash()
docker_client = docker.from_env()


class File:
    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.__hash = None

    @property
    def hash(self):
        if self.__hash is None:
            self.__hash = filehasher.hash_file(self.filename)  # TODO: worry about line endings
        return self.__hash

    def in_directory(self, directory):
        return os.path.commonpath([directory, self.filename]) == directory

    def __repr__(self):
        return self.filename


def get_working_tree_dir():
    repo = git.Repo('.', search_parent_directories=True)
    return repo.working_tree_dir


def get_files():
    git_client = git.Git()
    tracked_files = git_client.ls_files().split('\n')
    untracked_unignored_files = git_client.ls_files('--exclude-standard', '--others').split('\n')
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


def get_image_name(directory):
    with open(os.path.join(directory, 'image-name'), 'r') as f:
        return f.read().strip()


def write_image_tag(directory, image_tag):
    with open(os.path.join(directory, 'image-tag'), 'w') as f:
        f.write(image_tag)


def image_exists(image_tag):
    try:
        # TODO: Worry about the edge case where the image has been built but not pushed
        docker_client.images.get(image_tag)
        return True
    except docker.errors.ImageNotFound:
        try:
            # TODO: Find a faster way to do this...
            docker_client.images.get_registry_data(image_tag)
            return True
        except docker.errors.NotFound:
            return False


if __name__ == '__main__':
    os.chdir(get_working_tree_dir())

    files = get_files()

    if any(f.basename == 'image-tag' for f in files):
        sys.exit('image-tag needs to be in .gitignore')
    
    directories_to_build = get_directories_to_build(files)

    for directory in directories_to_build:
        combined_hash = get_combined_hash(get_directory_dependencies(files, directory))
        image_name = get_image_name(directory)
        image_tag = '{}:build-{}'.format(image_name, combined_hash[:12])
        
        if not image_exists(image_tag):
            print('Building {}...'.format(image_tag))
            print()
            builder = docker_client.api.build(path=directory, tag=image_tag, decode=True)
            for line in builder:
                if 'stream' in line:
                    print(line['stream'], end='')
            print()
            pusher = docker_client.images.push(image_tag, stream=True, decode=True)
            for line in pusher:
                if 'status' in line:
                    print(line['status'])
        else:
            print('Using cached {}...'.format(image_tag))

        write_image_tag(directory, image_tag)

