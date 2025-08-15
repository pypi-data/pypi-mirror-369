
.. image:: https://readthedocs.org/projects/which-bsm/badge/?version=latest
    :target: https://which-bsm.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/which_bsm-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/which_bsm-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/which_bsm-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/which_bsm-project

.. image:: https://img.shields.io/pypi/v/which-bsm.svg
    :target: https://pypi.python.org/pypi/which-bsm

.. image:: https://img.shields.io/pypi/l/which-bsm.svg
    :target: https://pypi.python.org/pypi/which-bsm

.. image:: https://img.shields.io/pypi/pyversions/which-bsm.svg
    :target: https://pypi.python.org/pypi/which-bsm

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/which_bsm-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/which_bsm-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://which-bsm.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/which_bsm-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/which_bsm-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/which_bsm-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/which-bsm#files


Welcome to ``which_bsm`` Documentation
==============================================================================
.. image:: https://which-bsm.readthedocs.io/en/latest/_static/which_bsm-logo.png
    :target: https://which-bsm.readthedocs.io/en/latest/

``which_bsm`` is a factory for creating boto session managers with environment-aware AWS authentication across local, CI/CD, and cloud runtimes. It automatically selects the appropriate authentication method based on where your code is running - whether that's local development with AWS CLI profiles, CI/CD environments using role assumption, or AWS compute services with built-in IAM roles.

The library simplifies multi-environment AWS deployments by providing a single configuration point that adapts to different runtime contexts. You configure your environment topology once, and the system handles authentication complexity automatically.

Key features include lazy-loaded session management, AWS account ID validation, automatic workload role ARN generation for CI environments, and runtime detection across various AWS services (Lambda, Batch, ECS, Glue, EC2) and CI platforms.


.. _install:

Install
------------------------------------------------------------------------------

``which_bsm`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install which-bsm

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade which-bsm
