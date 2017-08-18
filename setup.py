#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from os import environ as env
import subprocess

from pip.req import parse_requirements

requirements = [str(req.req) for req in parse_requirements('requirements.txt', session=False)]

try:
    VERSION = subprocess.check_output(['git', 'describe', '--tags']).strip()
except subprocess.CalledProcessError:
    VERSION = '0.dev'

setup(
    name='chatery',
    version=VERSION,
    description="Lightweight Chat application"
                " - with Twitter Support",
    long_description=open('README.md').read(),
    author="Shaurya-Xoxzo",
    author_email='shauryadeepc@hotmail.com',
    url='http://www.xoxzo.com',
    license='MIT',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'chatery = app:main',
        ],
    },
    zip_safe=False
)
