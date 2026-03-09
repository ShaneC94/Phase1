from setuptools import setup, find_packages

setup(
    name="ngsim_pipeline",
    version="0.1",
    packages=find_packages(),
    py_modules=["pipeline", "preprocessing", "scenarios"],
)