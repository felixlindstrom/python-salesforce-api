#!/usr/bin/env python
import os
from glob import glob
from setuptools import setup, find_packages


def data_files_inventory():
    data_files = []
    data_roots = ['salesforce_api/data']
    for data_root in data_roots:
        for root, subfolder, files in os.walk(data_root):
            files = [x.replace('salesforce_api/', '') for x in glob(root + '/*')
                     if not os.path.isdir(x)]
            data_files = data_files + files
    return data_files


PACKAGE_DATA = {'salesforce_api': data_files_inventory()}


if __name__ == '__main__':
    setup(
        name="salesforce-api",
        version='0.1.37',
        author="Felix Lindstrom",
        author_email='felix.lindstrom@gmail.com',
        description="Salesforce API wrapper",
        long_description=open('README.md').read(),
        long_description_content_type="text/markdown",
        keywords=['salesforce', 'salesforce api', 'salesforce bulk api'],
        license='MIT',
        packages=find_packages(exclude=['docs', 'tests*']),
        package_data=PACKAGE_DATA,
        include_package_data=True,
        install_requires=[
            'requests',
            'xmltodict',
            'url-normalize'
        ],
        zip_safe=True,
        url='https://github.com/felixlindstrom/python-salesforce-api',
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )