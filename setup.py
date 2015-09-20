try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'After the Deadline command-line tool',
    'author': 'Leandro Penz',
    'url': 'https://github.com/lpenz/atdtool',
    'author_email': 'lpenz@lpenz.org',
    'version': '1.3',
    'packages': ['atdtool'],
    'scripts': ['bin/atdtool'],
    'name': 'atdtool'
}

setup(**config)
