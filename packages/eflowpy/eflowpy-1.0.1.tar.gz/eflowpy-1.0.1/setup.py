from setuptools import setup, find_packages

# Read the README.md file as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eflowpy",
    version="1.0.1",
    description="A Python package for estimating environmental flow requirements using hydrological methods.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gokhan Cuceloglu",
    author_email="cuceloglugokhan@gmail.com",
    url="https://github.com/gokhancuceloglu/eflowpy",
    packages=find_packages(),
    install_requires=["pandas", "numpy", "matplotlib", "scipy"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)