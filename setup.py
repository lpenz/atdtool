#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re


def version_get():
    with open('atdtool/__init__.py') as fd:
        for line in fd:
            m = re.match('^PROGRAM_VERSION = "(?P<version>[0-9.]+)"',
                         line)
            if m:
                return m.group('version')


setup(name="atdtool",
      version=version_get(),
      description='After the Deadline command-line tool',
      author="Leandro Lisboa Penz",
      author_email="lpenz@lpenz.org",
      url="http://github.com/lpenz/atdtool",
      data_files=[('man/man1', ['atdtool.1'])],
      packages=['atdtool'],
      scripts=["bin/atdtool"],
      long_description="""\
atdtool is a command-line tools that contacts an After the Deadline language
service and displays the errors reported by the service in a format very
similar to gcc's.
""",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'License :: OSI Approved :: '
          'GNU General Public License v2 or later (GPLv2+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          ],
      license="GPL2")
