#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'mylibtool'
DESCRIPTION = 'My python library package with some scraper tool and data tool'
URL = 'https://github.com/pgshow/mylibtool'
EMAIL = 'me@example.com'
AUTHOR = 'Daniel'
REQUIRES_PYTHON = '>=3.10.0'
VERSION = '0.2.0'

# What packages are required for this module to be executed?
REQUIRED = [
    "addict==2.4.0",
    # Py>=3.9 自带 zoneinfo：仅在老版本 Python 才需要 backports
    'backports.zoneinfo==0.2.1; python_version < "3.9"',
    "carehttp>=0.3.11",
    "certifi==2022.5.18.1",
    "charset-normalizer==2.0.12",
    "colorama==0.4.4",
    "date-extractor==5.1.5",
    "dateparser==1.1.1",
    "filetype==1.0.13",
    "humanize==4.1.0",
    "idna>=2.8",
    "loguru==0.6.0",
    # ⚠️ maya 长期未维护，Py3.10 上常见问题较多，建议尽量不再依赖
    "maya==0.6.1",
    "pendulum==2.1.2",
    "python-dateutil==2.8.2",
    "pytz==2022.1",
    "pytz-deprecation-shim==0.1.0.post0",
    "pytzdata==2020.1",
    "regex==2022.3.2",
    "requests>=2.22.0",
    "requests-toolbelt>=1.0.0",
    "retrying==1.3.3",
    "six==1.16.0",
    "snaptime==0.2.4",
    # zoneinfo 在 Windows 往往需要 tzdata；限制到 Windows 平台安装
    'tzdata==2022.1; platform_system == "Windows"',
    "tzlocal==4.2",
    "urllib3>=1.25.8,<2",
    'win32-setctime==1.1.0; sys_platform == "win32"',
    "arrow~=1.2.2",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution…')
        os.system('{0} -m build'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # 二选一：包结构(project/包目录)用 packages；单文件模块用 py_modules。
    # 如果你的仓库里是包目录(最常见)，请移除 py_modules：
    # py_modules=['mylibtool'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
