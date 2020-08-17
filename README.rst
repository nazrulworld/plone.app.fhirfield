.. image:: https://img.shields.io/pypi/status/plone.app.fhirfield.svg
    :target: https://pypi.python.org/pypi/plone.app.fhirfield/
    :alt: Egg Status

.. image:: https://img.shields.io/travis/nazrulworld/plone.app.fhirfield/master.svg
    :target: http://travis-ci.org/nazrulworld/plone.app.fhirfield
    :alt: Travis Build Status

.. image:: https://coveralls.io/repos/github/nazrulworld/plone.app.fhirfield/badge.svg?branch=master
    :target: https://coveralls.io/github/nazrulworld/plone.app.fhirfield?branch=master
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

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black


Background (plone.app.fhirfield)
================================

`FHIR`_ (Fast Healthcare Interoperability Resources) is the industry standard for Healthcare system. Our intend to implement `FHIR`_ based system using `Plone`_! `plone.app.fhirfield`_ will make life easier to create, manage content for `FHIR resources`_ as well search facilities for any FHIR Resources.

How It Works
------------

This field is working as like other `zope.schema <https://zopeschema.readthedocs.io/en/latest/>`_ field, just add and use it. You will feed the field value as either json string or python dict of `FHIR`_ resources through web form or any restapi client. This field has built-in `FHIR`_ resource validator and parser.

Example::

    from plone.app.fhirfield import FhirResource
    from plone.supermodel import model

    class IMyContent(model.Schema):

        <resource_type>_resource = FhirResource(
            title=u'your title',
            desciption=u'your desciption',
            fhir_release='any of FHIR release name'
            resource_type='any fhir resource type[optional]'
        )

The field's value is the instance of a specilized class `FhirResourceValue` inside the context, which is kind of proxy class of `fhir model <https://pypi.org/project/fhir.resources/>`_ with additional methods and attributes.


Features
--------

- Plone restapi support
- Widget: z3cform support
- plone.supermodel support
- plone.rfc822 marshaler field support

Available Field's Options
=========================

This field has got all standard options (i.e `title`, `required`, `desciption` and so on) with additionally options for the purpose of either validation or constraint those are related to `FHIR`_.


fhir_release
    Required: Yes

    Default: None

    Type: String

    The release version of `FHIR`_

    Example: ``R4``, ``STU3``


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


index_mapping
    Required: No

    Default: None

    Type: JSON

    The custom index mapping, best case is elasticsearch mapping. Default mapping would be replaced by custom.

Field's Value API
=================

Field's value is a specilized class `plone.app.fhirfield.value.FhirResourceValue` which has reponsibilty to act as proxy of `fhirclient model's class <https://github.com/smart-on-fhir/client-py>`_. This class provides some powerful methods.

FhirResourceValue::json

    Originally this method is derived from fhir base model, you will always have to use this method during negotiation (although our serializer doing that for you automatically). This method not takes any argument, it returns FHIR json representation of resource.


FhirResourceValue::patch

    If you are familar with `FHIRPath Patch <https://www.hl7.org/fhir/fhirpatch.html>`_, this method one of the strongest weapon of this class. Patch applying on any `FHIR`_ resources is noting but so easy.
    This method takes one mandatory argument `patch_data` and that value should be list of patch items (`jsonpatch <http://jsonpatch.com/>`_).

    Example::

        from plone.app.fhirfield import FhirResource
        from plone.supermodel import model

        class ITask(model.Schema):

            resource = FhirResource(
                title=u'your title',
                desciption=u'your desciption',
                resource_type='Task'
            )

        patch_data = [
          {'op': 'replace', 'path': '/source/display', 'value': 'Patched display'},
          {'op': 'replace', 'path': '/status', 'value': 'Reopen'}
        ]
        task_content.resource.patch(patch_data)


FhirResourceValue::stringify

    This method returns string representation of fhir resource json value. Normally `as_json` returns python's dict type data. This method takes optional `prettify` argument, by setting this argument True, method will return human/print friendly representation.

FhirResourceValue::foreground_origin

    There may some situation come, where you will need just pure instance of fhir model, this method serves that purpose. This method returns current fhir resource model's instance.

    Example::

        from fhirclient.models.task import Task
        from plone.app.fhirfield import FhirResource
        from plone.supermodel import model

        class ITask(model.Schema):

            resource = FhirResource(
                title=u'your title',
                desciption=u'your desciption',
                resource_type='Task'
            )

        task = task_content.resource.foreground_origin()
        assert isinstance(task, Task)


Installation
============

Install plone.app.fhirfield by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.app.fhirfield


and then running ``bin/buildout``. Go to plone control and install ``plone.app.fhirfield`` or If you are creating an addon that depends on this product, you may add ``<dependency>profile-plone.app.fhirfield:default</dependency>`` in ``metadata.xml`` at profiles.



Links
=====

Code repository:

    https://github.com/nazrulworld/plone.app.fhirfield

Continuous Integration:

    https://travis-ci.org/nazrulworld/plone.app.fhirfield

Issue Tracker:

    https://github.com/nazrulworld/plone.app.fhirfield/issues

set max_map_count value (Linux)

```
sudo sysctl -w vm.max_map_count=262144
```

License
=======

The project is licensed under the GPLv2.

.. _`FHIR`: https://www.hl7.org/fhir/overview.html
.. _`Plone`: https://www.plone.org/
.. _`FHIR Resources`: https://www.hl7.org/fhir/resourcelist.html
.. _`Plone restapi`: http://plonerestapi.readthedocs.io/en/latest/
.. _`plone.app.fhirfield`: https://pypi.org/project/plone.app.fhirfield/
.. _`jmespath`: https://github.com/jmespath/jmespath.py
.. _`jsonpath-rw`: http://jsonpath-rw.readthedocs.io/en/latest/
.. _`jsonpath-ng`: https://pypi.python.org/pypi/jsonpath-ng/1.4.3
