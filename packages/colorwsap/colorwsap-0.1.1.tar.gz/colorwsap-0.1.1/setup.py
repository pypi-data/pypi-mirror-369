from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="colorwsap",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["opencv-python", "numpy"],
    description="Swap PNG logo colors easily by name or RGB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Karan Bedi",
    python_requires=">=3.6",
)
