import pathlib
import sys
import platform
from setuptools import setup

MAJOR = 0
MINOR = 1
MICRO = 0
ISRELEASED = True
VERSION = f'{MAJOR}.{MINOR}.{MICRO}'

min_version = (3, 6, 0)


def is_right_py_version(min_py_version):
    if sys.version_info < (3,):
        sys.stderr.write(
            'Python 2 has reached end-of-life and is no longer supported by Caer.')
        return False

    if sys.version_info < min_py_version:
        python_min_version_str = '.'.join((str(num) for num in min_py_version))
        no_go = f'You are using Python {platform.python_version()}. Python >={python_min_version_str} is  required.'
        sys.stderr.write(no_go)
        return False

    return True


if not is_right_py_version(min_version):
    sys.exit(-1)

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
with open(HERE / "README.md") as fh:
    README = fh.read()

# This call to setup() does all the work
setup(
    name="kwargshelper",
    version=VERSION,
    description="Manages testing for valid kwargs key, values pairs and assigns class attributes for pairs.",
    long_description_content_type="text/markdown",
    long_description=README,
    url="https://github.com/Amourspirit/python-kwargshelper",
    author=":Barry-Thomas-Paul: Moss",
    license="MIT",
    package_dir={'': 'src'},
    py_modules=['kwargs_util', 'kwarg_rules'],
    keywords=['python', 'kwargs', 'args', 'parse', 'helper'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
