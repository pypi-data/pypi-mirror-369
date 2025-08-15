#coding: utf-8
from __future__ import absolute_import
import os
from setuptools import setup, find_packages


def read(file_path):
    with open(file_path, 'r') as infile:
        return infile.read()


setup(name='m3-registry',
      version='2.3.0',
      url='https://bitbucket.org/barsgroup/registry',
      license='MIT',
      author='BARS Group',
      author_email='bars@bars-open.ru',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      description=read('DESCRIPTION.rst'),
      long_description=read('README.rst'),
      long_description_content_type='text/x-rst',
      install_requires=(
            'm3-django-compat>=1.5.1',
            'six >= 1.10.0',
      ),
      include_package_data=True,
      classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
      ],
)
