import os
import setuptools

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# install locally via `pip install -e .` (-> for development)
# install from github via `pip install git+https://github.com/MHubAI/mhubio (-> in Dockerfiles)

setuptools.setup(
    name = "segdb",
    version = "0.0.2",
    author = "Leonard Nürnberg",
    author_email = "lnuernberg@bwh.harvard.edu",
    description = ("Database for uniform body segmentation."),
    license = "MIT",
    keywords = "mhub",
    url = "https://github.com/MHubAI/SegDB",
    packages=setuptools.find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    package_data={'': ['data/*.csv']},
    install_requires=[
        "pandas" # pandas==1.5.2
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)
