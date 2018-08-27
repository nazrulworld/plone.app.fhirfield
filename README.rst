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
            resource_type='any fhir resource type[optional]'
        )

The field's value is the instance of a specilized class `FhirResourceValue` inside the context, which is kind of proxy class of `fhirclient model <https://github.com/smart-on-fhir/client-py>`_ with additional methods and attributes.

**Make field indexable**

A specilized Catalog PluginIndexes is named ``FhirFieldIndex`` is available, you will use it as like other catalog indexes. However importantly you have to maintain a strict convention (index name must be started with any valid fhir resource name (no matter uppercase or lowercase) and should _(underscore) be used as separator, i.e task_index(<resource>_<any name>))

Example::

    <?xml version="1.0"?>
    <object name="portal_catalog" meta_type="Plone Catalog Tool">
        <index name="organization_resource" meta_type="FhirFieldIndex">
            <indexed_attr value="organization_resource"/>
        </index>
    </object>


Features
--------

- Plone restapi support
- Widget: z3cform support
- plone.supermodel support
- plone.rfc822 marshaler field support
- `100% FHIR search compliance <https://www.hl7.org/fhir/search.html>`_ catalog search.


Available Field's Options
=========================

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


Field's Value API
=================

Field's value is a specilized class `plone.app.fhirfield.value.FhirResourceValue` which has reponsibilty to act as proxy of `fhirclient model's class <https://github.com/smart-on-fhir/client-py>`_. This class provides some powerful methods.

FhirResourceValue::as_json

    Originally this method is derived from fhirclient base model, you will always have to use this method during negotiation (although our serializer doing that for you automatically). This method not takes any argument, it returns FHIR json representation of resource.


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


Helper API
==========

This package provides some useful functions those could be usable in your codebase.

`resource_type_str_to_fhir_model`

    This function return appropriate `fhirclient model <https://github.com/smart-on-fhir/client-py>`_ class based on provided `resource type`. On wrong resource type `zope.interface.Invalid` exception is raisen.

    Example::

        >>> from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
        >>> task_model_class = resource_type_str_to_fhir_model('Task')


elasticsearch setup
===================

If your intent to use elasticsearch based indexing and query, this section for you! you can `find more details here <http://collectiveelasticsearch.readthedocs.io/en/latest/>`_

server setup
------------

server version is restricted to `2.4.x`, means we cannot use latest version of elasticsearch. i.e 5.6.x

- `Download from here <https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-6>`_ and install according to documentation.
- For development you could use docker container. The Makefile is available, `~$ make run-es`


collective.elasticsearch setup
------------------------------

Full configuration `guide could be found here <http://collectiveelasticsearch.readthedocs.io/en/latest/config.html#basic-configuration>`_. Simple steps are described bellow.

1. **create catalog/indexes**: First you will need add indexes for each fhirfield used in your project. each resource type has it's own Meta Index. `example is here <https://github.com/nazrulworld/plone.app.fhirfield/blob/master/src/plone/app/fhirfield/profiles/testing/catalog.xml>`_

2. Install `collective.elasticsearch` addon from plone control panel.

3. Convert your Indexes to elasticsearch. Go To `{portal url}/@@elastic-controlpanel`

4. In the settings form's `Indexes for which all searches are done through ElasticSearch` section add your all indexes those you mentioned into catalog.xml file, also add `portal_type`

5. Now save and again `Convert Catalog`.



Installation
============

Install plone.app.fhirfield by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.app.fhirfield [elasticsearch]


and then running ``bin/buildout``. Go to plone control and install ``plone.app.fhirfield`` or If you are creating an addon that depends on this product, you may add ``<dependency>profile-plone.app.fhirfield:default</dependency>`` in ``metadata.xml`` at profiles.

configuration
-------------

This product provides three plone registry based records ``fhirfield.es.index.mapping.nested_fields.limit``, ``fhirfield.es.index.mapping.depth.limit``, ``fhirfield.es.index.mapping.total_fields.limit``. Those are related to ElasticSearch index mapping setup, if you aware about it, then you have option to modify from plone control panel (Registry).



Links
=====

Code repository:

    https://github.com/nazrulworld/plone.app.fhirfield

Continuous Integration:

    https://travis-ci.org/nazrulworld/plone.app.fhirfield

Issue Tracker:

    https://github.com/nazrulworld/plone.app.fhirfield/issues



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