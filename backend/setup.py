#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages
from setuptools.command.install import install as st_install

import os
import shutil

try:
    from pypandoc import convert
except ImportError:
    def convert(filename, fmt):
        with open(filename) as fd:
            return fd.read()


class install(st_install):
    def _post_install(self, lib_dir):
        packages = ('page_builder',)
        backend_dir = os.path.join(lib_dir, 'backend')
        if os.path.exists(backend_dir):
            for package in packages:
                src_dir = os.path.join(backend_dir, package)
                dst_dir = os.path.join(lib_dir, package)
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir, symlinks=True)
            if os.path.exists(backend_dir):
                shutil.rmtree(backend_dir)
    def run(self):
        st_install.run(self)
        self.execute(self._post_install, (self.install_lib,),
                     msg="Running post install task")


CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="InfoLabs LLC",
    author_email="team@infolabs.ru",
    name="django-page-builder",
    version='0.1.0',
    description="Django Page Builder",
    long_description=convert('README.md', 'rst'),
    url='https://bitbucket.org/info-labs/django-page-builder.git',
    license='GPL v3 License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    package_dir={'page_builder': 'backend/page_builder'},
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': install},
    install_requires=[
        'Django>=1.9,<1.10',
        'django-classy-tags>=0.7.2,<0.7.3',
    ],
)
