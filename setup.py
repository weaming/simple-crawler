# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import os
import re

here = os.path.abspath(os.path.dirname(__file__))


def read_text(fname):
    if os.path.isfile(fname):
        with open(os.path.join(here, fname)) as f:
            return f.read()
    else:
        print("warning: file {} does not exist".format(fname))
        return ""


def get_version(path):
    src = read_text(path)
    pat = re.compile(r"""^version = ['"](.+?)['"]$""", re.MULTILINE)
    result = pat.search(src)
    version = result.group(1)
    return version


long_description = read_text("README.md")
install_requires = [
    l
    for l in read_text("requirements.txt").split("\n")
    if l.strip() and not l.strip().startswith("#")
]

name = "simple-crawler"
gh_repo = "https://github.com/weaming/{}".format(name)

setup(
    name=name,  # Required
    version=get_version("simple_crawler.py"),  # Required
    # This is a one-line description or tagline of what your project does.
    description="my simple crawler",  # Required
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    install_requires=install_requires,
    py_modules=['simple_crawler'],
    url=gh_repo,  # Optional
    author="weaming",  # Optional
    author_email="garden.yuen@gmail.com",  # Optional
    keywords="crawler",  # Optional
    project_urls={"Bug Reports": gh_repo, "Source": gh_repo},  # Optional
)

