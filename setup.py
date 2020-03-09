#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='layer-loader',
    version='0.0.1',
    url='https://github.com/PeterJCLaw/layer-loader',
    project_urls={
        'Documentation':
            'https://github.com/PeterJCLaw/layer-loader/blob/master/READNE.md',
        'Code': 'https://github.com/PeterJCLaw/layer-loader',
        'Issue tracker': 'https://github.com/PeterJCLaw/layer-loader/issues',
    },
    description="Easy composition of configuration files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'layer_loader': ['py.typed']},
    author="Peter Law",
    author_email='PeterJCLaw@gmail.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    test_suite='tests',
    zip_safe=True,
)
