README
======

.. image:: https://codecov.io/gh/Amourspirit/python-kwargshelper/branch/master/graph/badge.svg?token=mJ2HdGwSGy
    :target: https://codecov.io/gh/Amourspirit/python-kwargshelper
    :alt: codecov

.. image:: https://img.shields.io/github/workflow/status/Amourspirit/python-kwargshelper/CodeCov
    :alt: GitHub Workflow Status

.. image:: https://img.shields.io/github/license/Amourspirit/python-kwargshelper
    :alt: License MIT

.. image:: https://img.shields.io/pypi/pyversions/kwargshelper
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/wheel/kwargshelper
    :alt: PyPI - Wheel

kwargshelper
------------

A python package for working with **kwargs**

Installation
++++++++++++

You can install the Version Class from `PyPI <https://pypi.org/project/kwargshelper/>`_

.. code-block:: bash

    pip install kwargshelper

KwargsHelper Class
++++++++++++++++++

Helper class for working with python ``**kwargs`` in a class constructor

Assigns values of ``**kwargs`` to an exising class with type checking and rules

Parse kwargs with suport for rules that can be extended that validate any arg of kwargs.
Type checking of any type.

Callback function for before update that includes a Cancel Option.

Many other options avaliable for more complex usage.

KwArg Class
+++++++++++

Helper class for working with python ```**kwargs`` in a method/function
Wrapper for ``KwargsHelper`` Class.

Assigns values of ``**kwargs`` to itself with validation

Parse kwargs with suport for rules that can be extended that validate any arg of kwargs.
Type checking of any type.

Callback function for before update that includes a Cancel Option.

Many other options avaliable for more complex usage.