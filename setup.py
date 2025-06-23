"""  setup script."""

from os import path
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pydreo-cloud',
    packages = ['dreo'],
    include_package_data=True,
    version = '0.0.3',
    license='MIT',
    description = 'Library to login to Dreo cloud, get device list and device status information.',
    author = 'Brooke Wang',
    author_email = 'developer@dreo.com',
    url = 'https://github.com/dreo-team/pydreo-cloud',
    download_url = 'https://github.com/dreo-team/pydreo-cloud/archive/refs/tags/0.0.3.tar.gz',
    install_requires=[
        'requests',
        'tzlocal',
        'click',
        'pycryptodome'
    ],
    entry_points='''
        [console_scripts]
        dreo=dreo.cli:cli
    ''',
)