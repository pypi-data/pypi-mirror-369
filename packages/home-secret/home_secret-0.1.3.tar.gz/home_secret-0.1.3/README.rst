
.. image:: https://readthedocs.org/projects/home-secret/badge/?version=latest
    :target: https://home-secret.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/home_secret-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/home_secret-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/home_secret-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/home_secret-project

.. image:: https://img.shields.io/pypi/v/home-secret.svg
    :target: https://pypi.python.org/pypi/home-secret

.. image:: https://img.shields.io/pypi/l/home-secret.svg
    :target: https://pypi.python.org/pypi/home-secret

.. image:: https://img.shields.io/pypi/pyversions/home-secret.svg
    :target: https://pypi.python.org/pypi/home-secret

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/home_secret-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/home_secret-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://home-secret.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/home_secret-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/home_secret-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/home_secret-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/home-secret#files


Welcome to ``home_secret`` Documentation
==============================================================================
.. image:: https://home-secret.readthedocs.io/en/latest/_static/home_secret-logo.png
    :target: https://home-secret.readthedocs.io/en/latest/

Modern software development presents an increasingly complex credential management challenge. As cloud services proliferate and microservice architectures become standard, developers face exponential growth in sensitive information requiring secure storage and convenient access—API keys, database credentials, authentication tokens, and service endpoints.

This complexity creates a fundamental tension: developers need immediate access to credentials during development while maintaining rigorous security standards. Traditional approaches, from hardcoded secrets to scattered environment variables, fail to address the sophisticated demands of contemporary multi-platform, multi-account development workflows.

The consequences of inadequate credential management extend beyond inconvenience. Security breaches, development inefficiencies, and maintenance nightmares plague teams using fragmented approaches. What developers need is a systematic solution that unifies security, accessibility, and scalability into a coherent framework.

HOME Secret emerges as a response to these challenges—a comprehensive local credential management system built on structured JSON configuration and intelligent Python integration. This approach transforms credential management from a necessary evil into a streamlined development asset.

**Quick Links**

- `Comprehensive Document <https://github.com/MacHu-GWU/home_secret-project/blob/main/home-secret-a-unified-approach-to-local-development-credential-management.md>`_
- `Home secret core source code <https://github.com/MacHu-GWU/home_secret-project/blob/main/home_secret/home_secret.py>`_
- `Sample home_secret.json file <https://github.com/MacHu-GWU/home_secret-project/blob/main/home_secret/home_secret.json>`_


.. _install:

Install
------------------------------------------------------------------------------

``home_secret`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install home-secret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade home-secret
