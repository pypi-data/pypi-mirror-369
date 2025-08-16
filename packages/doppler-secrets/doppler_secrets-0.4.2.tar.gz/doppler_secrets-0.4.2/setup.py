# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doppler']

package_data = \
{'': ['*']}

install_requires = \
['cachetools>=6.1.0,<7.0.0', 'pyjson5>=1.6.9,<2.0.0', 'requests>=2.32.4,<3.0.0']

setup_kwargs = {
    'name': 'doppler-secrets',
    'version': '0.4.2',
    'description': 'Dead simple Doppler client',
    'long_description': 'doppler-secrets\n===============\n\n\n',
    'author': 'Fede Calendino',
    'author_email': 'fede@calendino.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/fedecalendino/doppler-secrets',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
