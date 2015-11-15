try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'An indexation server/query API for the DIP protocol',
    'author': 'Frank Denis',
    'url': 'https://github.com/jedisct1/eris',
    'download_url': 'https://github.com/jedisct1/eris',
    'author_email': 'github@pureftpd.org',
    'version': '0.1',
    'install_requires': [
      'nose', 'validate_email', 'flask_arango', 'ujson', 'pyblake2',
      'flask_swagger', 'python-arango'
    ],
    'packages': ['eris'],
    'scripts': [],
    'name': 'eris'
}

setup(**config)
