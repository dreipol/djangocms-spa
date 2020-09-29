#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
from io import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from djangocms_spa/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("djangocms_spa", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst', 'r', encoding='utf-8').read()
history = open('HISTORY.rst', 'r', encoding='utf-8').read().replace('.. :changelog:', '')

setup(
    name='djangocms-spa',
    version=version,
    description="""Run your django CMS project as a single-page application (SPA)""",
    long_description=readme + '\n\n' + history,
    author='dreipol GmbH',
    author_email='dev@dreipol.ch',
    url='https://github.com/dreipol/djangocms-spa',
    packages=[
        'djangocms_spa',
    ],
    include_package_data=True,
    install_requires=[
        'django>=2.2',
        'django-cms>=3.0',
        'djangorestframework>=3.5.0',
        'django-appconf>=1.0.1',
        'requests>=2'
    ],
    license="MIT",
    zip_safe=False,
    keywords='djangocms-spa',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
