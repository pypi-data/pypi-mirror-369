# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graph_id', 'graph_id.analysis', 'graph_id.commands', 'graph_id.core']

package_data = \
{'': ['*']}

install_requires = \
['pybind11==2.11.1', 'pymatgen>=2025.4.20,<2026.0.0', 'scikit-learn>=0.24.1']

setup_kwargs = {
    'name': 'graph-id-core',
    'version': '0.1.4',
    'description': '',
    'long_description': '\n\n# Graph ID\n\n## Installation \n\n### From pypi\n\n```\npip install graph-id-core\npip install graph-id-db # optional\n```\n\n### From GitHub\n\n```\ngit clone git+https://github.com/kmu/graph-id-core.git\ngit submodule init\ngit submodule update\npip install -e .\n```\n',
    'author': 'Koki Muraoka',
    'author_email': 'muraok_k@chemsys.t.u-tokyo.ac.jp',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.14',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
