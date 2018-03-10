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

Background (plone.app.fhirfield)
================================

`FHIR`_ (Fast Healthcare Interoperability Resources) is the standard for Healthcare system. Our intend to implemnt `FHIR`_ based system using `Plone`_! `plone.app.fhirfield`_ will make life easier to create, manage content for `FHIR resources`_.

Features
--------

- Plone restapi support
- Widget: z3cform support
- plone.supermodel support
- plone.rfc822 marshaler field support


Available Options
=================

This field has got all standard options (i.e `title`, `required`, `desciption` and so on) with additionally options for the purpose of either validation or constraint those are related to `FHIR`_.



resource_type
    Required: No

    Default: None

    Type: String

    The name of `FHIR`_ resource can be used as constraint, meaning that we can restricted only accept certain resource. If FHIR json is provided that contains other resource type, would raise validation error.
    Example: `FhirResource(....,resource_type='Patient')`

model
    Required: No

    Default: None

    Type: String + full python path (dotted) of the model class.

    Like `resource_type` option, it can be used as constraint, however additionally this option enable us to use custom model class other than fhirclient's model.
    Example: `FhirResource(....,model='fhirclient.models.patient.Patient')`

model_interface
    Required: No

    Default: None

    Type: String + full python path (dotted) of the model class.

    Unlike `model` option, this option has more versatile goal although you can use it for single resource restriction. The advanced usecase like, the field could accept muiltiple resources types those model class implements the provided interface. For example you made a interface called `IMedicalService` and (`Organization`, `Patient`, `Practitioner`) models those are implementing `IMedicalService`. So when you provides this option value, actually three types of fhir json can now be accepted by this field.
    Example: `FhirResource(....,model='plone.app.interfaces.IFhirResourceModel')`



Roadmaps
========

- indexing: we have plan to support json index like elastic search model. Ofcourse performance will be main issue. bellows are some libraries, I found. You are welcome to suggest me any better library for json search.
    - `jmespath`_
    - `jsonpath-ng`_
    - `jsonpath-rw`_
- elastic search support


Installation
============

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