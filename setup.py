
import os
from setuptools import setup, find_namespace_packages

version="0.0.1"

setup(
  name="mkdv",
  version=version,
  packages=find_namespace_packages(where='src'),
  package_dir={'' : 'src'},
  author="Matthew Ballance",
  author_email="matt.ballance@gmail.com",
  description=("mkdv is a Makefile-based mechanism for running Design Verification tools with a Python regression runner"),
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
    'colorama',
    'allure-python-commons',
    'markdown',
    'pyyaml'
  ],
)

