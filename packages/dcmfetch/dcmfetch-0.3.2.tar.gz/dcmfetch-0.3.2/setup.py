from setuptools import setup
from os.path import join, dirname, abspath
import sys
import unittest

# Single definition of version
__version__ = 'UNDEFINED'
# version.py should contain just the one line: __version__ = 'X.Y.Z'
with open(join(dirname(__file__), 'dcmfetch', 'version.py')) as f:
    exec(f.read())


def readme(fname):
    path = abspath(join(dirname(__file__), fname))
    with open(path, encoding='utf-8') as f:
        return f.read()


dependencies = [
    'requests>=2.2.5',
    'QtPy>=2.0.0',
    'pydicom>=2.2.2'
]

test_dependencies = [
    'cryptography',
    'pynetdicom'
]

setup(
    name='dcmfetch',
    version=__version__,
    description='DICOM query retrieve tools',
    long_description=readme('README.md'),
    long_description_content_type='text/markdown',
    author='Ron Hartley-Davies',
    author_email='R.Hartley-Davies@physics.org',
    url='https://bitbucket.org/rtrhd/dcmfetch',
    download_url='https://bitbucket.org/rtrhd/dcmfetch/get/v%s.zip' % __version__,
    license='MIT',
    install_requires=dependencies,
    tests_require=test_dependencies,
    extras_require={
        'PyNetDicom': 'pynetdicom>=2.1.1',
        'test': test_dependencies
    },
    packages=['dcmfetch'],
    entry_points={
        'console_scripts': ['dcmfetch = dcmfetch.dcmfetch:main'],
        'gui_scripts': ['dcmfetchtool = dcmfetch.dcmfetchtool:main']
    },
    package_data={
        'dcmfetch': ['ext/findscu*', 'ext/getscu*', 'ext/dcmnodes.cf', 'ext/store-tcs.properties']
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ]
)
