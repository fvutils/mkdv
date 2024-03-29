
import os
from setuptools import setup, find_namespace_packages

version="0.0.1"

if "BUILD_NUM" in os.environ.keys():
    version += "." + os.environ["BUILD_NUM"]

setup(
  name="mkdv",
  version=version,
  packages=find_namespace_packages(where='src'),
  package_dir={'' : 'src'},
  package_data={
      "mkdv": ["share/mkfiles/*"]
  },
  author="Matthew Ballance",
  author_email="matt.ballance@gmail.com",
  description=("mkdv is a Makefile-based mechanism for running Design Verification tools with a Python regression runner"),
  long_description="""
  mkdv provides a job-running system customized for running Design Verification jobs
  """,
  license="Apache 2.0",
  keywords = ["Python", "Functional Verification"],
  url = "https://github.com/fvutils/mkdv",
  entry_points={
    'console_scripts': [
      'mkdv = mkdv.__main__:main'
    ]
  },
  setup_requires=[
    'colorama',
    'pyyaml',
    'setuptools_scm',
    'wheel',
  ],
  install_requires=[
    'allure-python-commons',
    'colorama',
    'fusesoc',
    'jsonschema',
    'markdown',
    'pypyr>=5.3.0',
    'pyyaml',
    'toposort'
  ],
)

