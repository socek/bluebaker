# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'smallsettings',
    'formskit',
    'venusian',
    'gevent',
    'pyside',
    'greentree',
    'venusian',
    'mock',
]

dependency_links = [
    'https://github.com/socek/smallsettings/tarball/master#egg=smallsettings-0.1',
    'https://github.com/socek/formskit/tarball/master#egg=formskit-0.1',
    'https://github.com/socek/Gallifrey/tarball/master#egg=greentree-0.1',
]

if __name__ == '__main__':
    setup(name='BlueBaker',
          version='0.1',
          author=['Dominik "Socek" Długajczy'],
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          install_requires=install_requires,
          dependency_links=dependency_links,
          test_suite='bluebaker.tests.get_all_test_suite',
          )
