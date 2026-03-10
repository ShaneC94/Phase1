from setuptools import setup, find_packages

setup(
    name="ngsim_pipeline",
    version="0.1",
    install_requires=[
        "apache-beam[gcp]"
    ],
    packages=find_packages(),
    py_modules=[
        "pipeline",
        "scenario",
        "preprocessing",
        "visualization"
    ]
)
