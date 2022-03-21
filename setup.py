import os, sys, re

from slimjim import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(readme).read()


SETUP_ARGS = dict(
    name='slimjim',
    version=__version__,
    description=('Hackish keystroke injection tool '),
    long_description=long_description,
    url='https://github.com/cltrudeau/slimjim',
    author='Christopher Trudeau',
    author_email='ctrudeau+pypi@arsensa.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.10',
    ],
    py_modules = ['slimjim',],
    scripts=['bin/slimfile', 'bin/slimspec', ],
    install_requires = [
        'asciimatics>=1.13.0',
    ],
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
