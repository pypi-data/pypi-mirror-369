from setuptools import find_packages, setup

with open('readme.md', 'r') as f:
    description = f.read()

setup(
    name="pixBoards",
    version="0.2.7",
    packages=find_packages(),
    include_package_data=True,
    package_data={"pixBoards": ["templates/*.*"]},
    # install_requires = [
    # ]
    entry_points={
        "console_scripts": [
            "run=boards.cli:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)

"""
python3 setup.py sdist bdist_wheel
twine upload dist/*
"""
