import sys

import os.path

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--strict',
            '--verbose',
            '--tb=long',
            'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


INSTALL_REQUIRES=[
    'aiohttp>=3.3.2',
]


TEST_REQUIRES=[
    'pytest',
    'pytest-aiohttp',
]


setup(
    name='python-solarportal',
    version='1.0.0',
    description='SolarPortal API',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/StevenLooman/python-solarportal',
    author='Steven Looman',
    author_email='steven.looman@gmail.com',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['solarportal'],
    tests_require=TEST_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    cmdclass={'test': PyTest},
    scripts=[
        'bin/solarportal-to-csv',
        'bin/solarportal-to-pvoutput',
    ]
)
