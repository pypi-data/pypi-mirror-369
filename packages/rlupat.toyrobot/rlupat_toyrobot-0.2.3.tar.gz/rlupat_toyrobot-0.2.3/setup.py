from setuptools import setup, find_packages

# read the contents of README.md file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="rlupat.toyrobot",
    version="0.2.3",
    description="ToyRobot Example Implementation",
    author="Richard Lupat",
    license="MIT",
    packages=["toyrobot"]
    + ["toyrobot." + p for p in sorted(find_packages("./toyrobot"))],
    install_requires=[
        "wheel",
        "setuptools",
        "twine"
    ],
    entry_points={"console_scripts": ["toyrobot=toyrobot.app:main"]},
    zip_safe=False,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
