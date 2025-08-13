from setuptools import find_packages, setup

with open('readme.md', 'r') as f:
    description = f.read()

def parse_requirements(filename= "requirements.txt"):
    with open(filename, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pixBoards",
    version="0.2.12",
    packages=find_packages(),
    include_package_data=True,
    package_data={"pixBoards": ["templates/*.*"]},
    install_requires = parse_requirements(),
    entry_points={
        "console_scripts": [
            "run=boards.cli:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)

"""
git add . && git commit -m "fixes"
git push
python3 setup.py sdist bdist_wheel
twine upload dist/*
pypi-AgEIcHlwaS5vcmcCJDM2YWY1NDM1LWRlMzAtNGQxNy04YmI1LTIxNTE5ZjRiMTQ2YgACKlszLCI4NDc4NDAzYS1jMjE1LTQ0Y2MtOTg0My0xOGFiYjVlNzZiMjEiXQAABiDV8z06YKBMyyYBnTRJCWC6ACLq6lB3WyFgwziIQ6M9oA
"""
