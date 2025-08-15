from setuptools import setup, find_packages

setup(
    name="igprasad",  # must be unique
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["ig=ig.cli:main"],  # the command can still be `ig`
    },
    python_requires=">=3.10",
    description="Run predefined Python programs from cmd",
    author="Prasad Kamble",
)
