from setuptools import setup, find_packages

setup(
    name='monorepo-quickbuild-poc',
    packages=find_packages(),
    install_requires=['GitPython', 'docker', 'pyyaml', 'inflection'],
    entry_points={
        'console_scripts': {
            'quickbuild=quickbuild_poc:main'
        }
    },
    zip_safe=False
)

