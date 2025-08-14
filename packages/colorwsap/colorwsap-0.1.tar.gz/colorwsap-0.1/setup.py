from setuptools import setup, find_packages

setup(
    name="colorwsap",
    version="0.1",
    packages=find_packages(),
    install_requires=["opencv-python", "numpy"],
    description="Swap PNG logo colors easily by name or RGB",
    author="Your Name",
    python_requires=">=3.6",
)
