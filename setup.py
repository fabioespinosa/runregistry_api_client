import codecs
import os
import re
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open(os.path.join(here, "readme.md")) as f:
    long_description = f.read()

setup(
    name="runregistry",
    version=find_version("runregistry", "__init__.py"),
    packages=find_packages(),
    author="Fabio Espinosa",
    description="CMS Run Registry client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fabioespinosa/runregistryclient",
    author_email="f.e@cern.ch",
    install_requires=["requests", "cernrequests"]
)
