from setuptools import setup, find_packages

setup(
    name='mrpbuild-poc',
    packages=find_packages(),
    install_requires=['GitPython', 'docker', 'pyyaml', 'inflection'],
    entry_points={
        'console_scripts': {
            'mrpbuild=mrpbuild_poc:main'
        }
    },
    zip_safe=False
)

