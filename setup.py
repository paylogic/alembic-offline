"""Setup script for the `wsgi-statsd' package."""

import codecs
from os.path import abspath, dirname, join
import sys

from setuptools import setup

long_description = []

install_requires = ['alembic']

if sys.version_info < (3, 0, 0):
    install_requires.append('subprocess32')

tests_require = [
    "mock==1.0.1",
    "pylama==6.3.1",
    "pytest==2.7.0",
]

for text_file in ['README.rst', 'CHANGES.rst']:
    with codecs.open(join(dirname(abspath(__file__)), text_file), encoding='utf-8') as f:
        long_description.append(f.read())

setup(
    name="alembic-offline",
    description="Offline extensions for alemic database migration framework",
    long_description='\n'.join(long_description),
    author="Anatoly Bubenkov, Paylogic International and others",
    license="MIT license",
    author_email="developers@paylogic.com",
    url="https://github.com/paylogic/alembic-offline",
    version="1.0.4",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=["alembic_offline"],
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    alembic-offline = alembic.config:main
    """,
    tests_require=tests_require,
    extras_require=dict(test=tests_require)
)
