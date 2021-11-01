Install
=======


PIP
---

| ``kwargshelper`` from `PyPI <pypi_>`_:
| If you use pip, you can install ``kwargshelper`` with:

.. code:: bash

   pip install kwargshelper

Also when using pip, it’s good practice to use a virtual environment - see :ref:`Reproducible Installs <reproducible-installs>` below
for why, and `this guide <https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko#howto>`_ for details on using virtual environments.

.. _reproducible-installs:

REPRODUCIBLE INSTALLS
---------------------

As libraries get updated, results from running your code can change, or your code can break completely.
It’s important to be able to reconstruct the set of packages and versions you’re using. Best practice is to:

#. use a different environment per project you’re working on,
#. record package names and versions using your package installer; each has its own metadata format for this:

   * Conda: `conda environments and environment.yml <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#>`_
   * Pip: `virtual <https://docs.python.org/3/tutorial/venv.html>`_ environments and `requirements.txt <https://pip.readthedocs.io/en/latest/user_guide/#requirements-files>`_
   * Poetry: `virtual environments and pyproject.toml <https://python-poetry.org/docs/basic-usage/>`_

.. _pypi: https://pypi.org/project/kwargshelper/
