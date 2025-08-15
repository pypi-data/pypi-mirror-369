# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['foxops_client']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.24.1,<0.25.0',
 'structlog>=23.1.0,<24.0.0',
 'tenacity>=9.0.0,<10.0.0']

setup_kwargs = {
    'name': 'foxops-client',
    'version': '0.3.1',
    'description': 'Foxops API Client',
    'long_description': '# foxops-client-python\n\nThis repository contains the Python client for the [foxops](https://github.com/roche/foxops) templating tool.\n\n## Installation\n\n```shell\npip install foxops-client\n```\n\n## Usage\n\n```python\nfrom foxops_client import FoxopsClient, AsyncFoxopsClient\n\nclient = FoxopsClient("http://localhost:8080", "my-token")\nincarnations = client.list_incarnations()\n\n# or alternatively, the async version\nclient = AsyncFoxopsClient("http://localhost:8080", "my-token")\nincarnations = await client.list_incarnations()\n```\n',
    'author': 'Alexander Hungenberg',
    'author_email': 'alexander.hungenberg@roche.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
