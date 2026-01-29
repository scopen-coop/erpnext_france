import ast
import re

from setuptools import setup

# get version from __version__ variable in erpnext_france/__init__.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("erpnext_france/__init__.py", "rb") as f:
	version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

setup()
