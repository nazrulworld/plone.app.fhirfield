.. image:: https://img.shields.io/pypi/status/plone.app.fhirfield.svg
    :target: https://pypi.python.org/pypi/plone.app.fhirfield/
    :alt: Egg Status

.. image:: https://img.shields.io/travis/nazrulworld/plone.app.fhirfield/master.svg
    :target: http://travis-ci.org/nazrulworld/plone.app.fhirfield
    :alt: Travis Build Status

.. image:: https://img.shields.io/coveralls/nazrulworld/plone.app.fhirfield/master.svg
    :target: https://coveralls.io/r/nazrulworld/plone.app.fhirfield
    :alt: Test Coverage

.. image:: https://img.shields.io/pypi/pyversions/plone.recipe.sublimetext.svg
    :target: https://pypi.python.org/pypi/plone.recipe.sublimetext/
    :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/plone.app.fhirfield.svg
    :target: https://pypi.python.org/pypi/plone.app.fhirfield/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/plone.app.fhirfield.svg
    :target: https://pypi.python.org/pypi/plone.app.fhirfield/
    :alt: License


.. contents::

Introduction (plone.app.fhirfield)
==================================

`FHIR`_ (Fast Healthcare Interoperability Resources) is the standard for Healthcare system. Our intend to implemnt `FHIR`_ based system using `Plone`_! `plone.app.fhirfield`_ will make life easier to create, manage content for `FHIR resources`_.

Features
--------

- Plone restapi support
- Widget: z3cform support


Roadmaps
--------
- indexing: we have plan to support json index like elastic search model. Ofcourse performance will be main issue. bellows are some libraries, I found. You are welcome to suggest me any better library for json search.
    - `jmespath`_
    - `jsonpath-ng`_
    - `jsonpath-rw`_
- elastic search support


Installation
------------

Install plone.app.fhirfield by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.app.fhirfield


and then running ``bin/buildout``


Links
=====

Code repository:

    https://github.com/nazrulworld/plone.app.fhirfield

Continuous Integration:

    https://travis-ci.org/nazrulworld/plone.app.fhirfield

Issue Tracker:

    https://github.com/nazrulworld/plone.app.fhirfield/issues



License
-------

The project is licensed under the GPLv2.

.. _`FHIR`: https://www.hl7.org/fhir/overview.html
.. _`Plone`: https://www.plone.org/
.. _`FHIR Resources`: https://www.hl7.org/fhir/resourcelist.html
.. _`Plone restapi`: http://plonerestapi.readthedocs.io/en/latest/
.. _`plone.app.fhirfield`: https://pypi.python.org/pypi/plone.app.fhirfield/
.. _`jmespath`: https://github.com/jmespath/jmespath.py
.. _`jsonpath-rw`: http://jsonpath-rw.readthedocs.io/en/latest/
.. _`jsonpath-ng`: https://pypi.python.org/pypi/jsonpath-ng/1.4.3