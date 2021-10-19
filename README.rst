Welcome to kwargs’s docs!
=========================

|codecov| |gws| |lic| |pver| |pwheel|

kwargshelper
------------

A python package for working with **kwargs**.

Allows for validation of args passed in via ``**kwargs`` in various ways.
Such as type checking, rules checking, error handeling.

Many built in rules that make validation of input simple and effective.
Easily create and add new rules.

Various callbacks to hook each **kwarg** with rich set of options for fine control.

Docs
++++

Read the docs `here <https://python-kwargshelper.readthedocs.io/>`_

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

Helper class for working with python ``**kwargs`` in a method/function
Wrapper for ``KwargsHelper`` Class.

Assigns values of ``**kwargs`` to itself with validation

Parse kwargs with suport for rules that can be extended that validate any arg of kwargs.
Type checking of any type.

Callback function for before update that includes a Cancel Option.

Many other options avaliable for more complex usage.

.. |codecov| image:: https://codecov.io/gh/Amourspirit/python-kwargshelper/branch/master/graph/badge.svg?token=mJ2HdGwSGy
    :target: https://codecov.io/gh/Amourspirit/python-kwargshelper
    :alt: codecov

.. |gws| image:: https://img.shields.io/github/workflow/status/Amourspirit/python-kwargshelper/CodeCov
    :alt: GitHub Workflow Status

.. |lic| image:: https://img.shields.io/github/license/Amourspirit/python-kwargshelper
    :alt: License MIT

.. |pver| image:: https://img.shields.io/pypi/pyversions/kwargshelper
    :alt: PyPI - Python Version

.. |pwheel| image:: https://img.shields.io/pypi/wheel/kwargshelper
    :alt: PyPI - Wheel