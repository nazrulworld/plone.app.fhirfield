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


gzip_compression
    Required: No

    Default: False

    Type: Boolean

    Compressed version of json string will be stored into database.



Disclaimer!!
============

Do not directly access (get or set) field value from content object, unless you know, what you are doing. You should
always use field accessor to get or set value (examples are bellow). Because our expected field value would be ``FHIRModel``
from https://pypi.org/project/fhir.resources/ but in zodb raw json string or gzip compressed bytes is stored and don´t worry
about this complexity, Field accessor would take care for everything.

example 1: make accessor function into content class.::

    class IOrganization(model.Schema):

        organization_resource = FhirResource(
            title=u"Fhir Organization Field",
            resource_type="Organization",
            fhir_release="STU3",
        )

    @implementer(IOrganization)
    class Organization(Container):

        def get_organization_resource(self):
            return IOrganization["organization_resource"].get(self)


example 2: using datamanger accessor::

    >>> from zope.component import queryMultiAdapter
    >>> from z3c.form.interfaces import IDataManager
    >>> dm = queryMultiAdapter((content, fhirfield), IDataManager)
    >>> value = dm.get()
    >>> dm.set(new_value)


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
