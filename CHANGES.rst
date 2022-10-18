Changelog
=========

4.2.1 (2022-10-18)
------------------

Bugfixes

- `Issue-37: <https://github.com/nazrulworld/plone.app.fhirfield/issues/37>`_ Can not add a default value for fhirfield.


4.2.0 (2020-12-07)
------------------

Improvements

- Field deserializer is now accepting ``fhir.resources``'s model object, FhirResourceValue, alongside with string and dict type value.

- ``FhirResource::from_resource_model`` method has been added.

4.1.0 (2020-09-08)
------------------

Improvements

- Not any visibly improvement, but a lot of cleanup unused, unnecessary codes, in that impact made more slimmer version.

Breakings

- ``api`` module has been removed, use any import from ``plone.app.fhirfield`` instead.

- ``IFhirResourceModel`` interface is no longer available.

4.0.0 (2020-08-17)
------------------

Improvements

- supports `pydantic <https://pypi.org/project/pydantic/>`_ powered latest `fhir.resources <https://pypi.org/project/fhir.resources/>`_ via `fhirpath <https://pypi.org/project/fhirpath/>`_.
- suports Python 3.6.


Breakings

- Any FHIR search, FhirFieldIndex, EsFhirFieldIndex are removed. Please see `collective.fhirpath <https://pypi.org/project/collective.fhirpath/>`_ for those implementation.

- ``model_interface`` parameter has been removed from `FhirResource` field.

- Removed three ``fhirfield.es.index.mapping`` registry.

- extra option ``elasticsearch`` has been removed from setup.py


3.1.1 (2020-05-15)
------------------

- Nothing changed but some documents updated.


3.1.0 (2020-05-14)
------------------

Breakings

- Drop support python version until 3.6.x

- ``FhirResource.get_fhir_version`` been changed to ``FhirResource.get_fhir_release`` and no longer returns Enum member instead just string value.

- One of required ``FhirResource`` init parameter ``fhir_version`` has been changed to ``fhir_release``.

Removed Helper Functions

- ``plone.app.fhirfield.helpers.resource_type_str_to_fhir_model`` use ``fhirpath.utils.lookup_fhir_class``.

- ``plone.app.fhirfield.helpers.search_fhir_model`` use ``fhirpath.utils.lookup_fhir_class_path``

- ``plone.app.fhirfield.helpers.import_string`` use ``fhirpath.utils.import_string``


3.0.0 (2020-03-18)
------------------

Improvements

- Elasticsearch mappings are updated with correct value.


3.0.0b2 (2019-11-12)
--------------------

Newfeatures

- Fully compatiable with `collective.fhirpath`_.

- It is possible to provide custom index mapping through ``FhirResource`` field.

Breakings

- ``fhir_version`` value is manadatory, so you have provide fhir version number.

Deprecations

- Using PluginIndexes (EsFhirFieldIndex) has been deprecated.

- FHIR Search through ``portal_catalog`` has been deprecated.

- Using elasticsearch mapping from this project has been deprecated.


3.0.0b1 (2019-10-01)
--------------------

Newfeatures

- `FHIRPath`_ support added through `collective.fhirpath`_.

- Now supports Elasticsearch server version ``6.8.3``.


Breakings

- Drop support python 2.x.x.

2.0.0 (2019-05-18)
------------------

Newfeatures

- `Issue#14 <https://github.com/nazrulworld/plone.app.fhirfield/issues/14>`_ Now reference query is powerful yet!
  It is possible now search by resourceType only or mixing up.

- `Issue#21 <https://github.com/nazrulworld/plone.app.fhirfield/issues/21>`_ One of the powerful feature added, IN/OR support in search query.
  Now possible to provide multiple values separated by comma.

Breakings

- Drop support Elastic server version 2.3.x.


Bugfixes

- Important fix for ``Quantity`` search type, now value prefix not impact on other (unit, system). Additionally
  also now possible to search by unit or system and code (without value)


1.0.0 (2019-01-18)
------------------

Breaking

- Drop ``fhirclient`` dependency, instead make ``fhir.resources`` dependency.
- ``collective.elasticsearch`` version minimum version ``2.0.5`` has been pinned.


1.0.0rc4 (2018-10-25)
---------------------

Breaking

- Drop support for Plone 4.xx (sorry).

Improvements

- Issue#10 JSON Viewer added in display mode.

- Issue#18 `api` module to make available for all publicly usable methods, functions, classes.

- Issue#17 Add suports for duplicate param names into query string. It is now possible to provide multiple condition for same param type. For example `?_lastUpdated=gt2015-10-15T06:31:18+00:00&_lastUpdated=lt2018-01-15T06:31:18+00:00`

- Issue#10 Add support for `Composite` type FHIR search param.

- Issue#13 Add support for `Address` and `ContactPoint` mapping. It opens up many search params.

- Mappings are more enriched, so many missing mappings are added, like `valueString`, `valueQuantity` and so on.[nazrulworld]

- Issue#12 Full support for `code` search param type has been added, it also opens up for other search parameters (y).

- Issue#15 support for `Humanane` mapping in search.


1.0.0rc3 (2018-09-22)
---------------------

Improvements

- `Issue: 6 <https://github.com/nazrulworld/plone.app.fhirfield/issues/6>`_ A major improvement has been done, now very slim version (`id`, `resourceType`, `meta`) of FHIR json resource has been indexed in ZCatalog (zope index) version, however previously whole fhir resource was stored as a result now huge storage savings, perhaps improves indexing performance. [nazrulworld]


1.0.0rc2 (2018-08-29)
---------------------

Bugfixes

- Issue 5: `FHIR search's modifier 'missing' is not working for nested mapping <https://github.com/nazrulworld/plone.app.fhirfield/issues/5>`_

1.0.0rc1 (2018-08-27)
---------------------

Newfeatures

- `Identifier search parameter <http://www.hl7.org/fhir/search.html#token>`_ is active now (both array of identifier and single object identifier).

- Array of Reference query support (for example `basedOn` (list of reference) ) is active now. Although normal object reference has already been supported.

- All available mappings for searchable resources are generated.

- `FHIR search sort feature <https://www.hl7.org/fhir/search.html#sort>`_ is available!

- `fhirfield.es.index.mapping.nested_fields.limit`, `fhirfield.es.index.mapping.depth.limit` and `fhirfield.es.index.mapping.total_fields.limit` `registry records <https://pypi.org/project/plone.app.registry>`_ are `available to setup ES mapping <https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html#mapping-limit-settings>`_

- `URI` and `Number` type parameter based search are fully available.

- **`resourceType` filter is automatically injected into every generated query.** Query Builder knows about which resourceType should be.


Breaking Changes

- `plone.app.fhirfield` have to install, as some registry records (settings) for elasticsearch mapping have been introduced.

- Any deprecated FHIR Field Indexes other than `FhirFieldIndex` (`FhirOrganizationIndex` and so on) are removed


1.0.0b7 (2018-08-10)
--------------------

- `Media search available <https://www.hl7.org/fhir/media.html>`_.
- `plone.app.fhirfield.SearchQueryError` exception class available, it would be used to catch any fhir query buiding errors. [nazrulworld]


1.0.0b6 (2018-08-04)
--------------------

- Fix: minor type mistake on non existing method called.
- Migration guide has been added. [nazrulworld]


1.0.0b5 (2018-08-03)
--------------------

Newfeatures

- `FhirFieldIndex` Catalog Index has been refactored. Now this class is capable to handle all the FHIR resources. That's why other PluginIndexes related to FhirField have been deprecated.
- New ZCatalog (plone index) index naming convention has been introduced. Any index name for FhirFieldIndex must have fhir resource type name as prefix. for example: `task_index`


1.0.0b4 (2018-08-01)
--------------------

- Must Update (fix): Important updates made on mapping, reference field mapping was not working if value contains with `/`, now made it tokenize by indecating index is `not_analyzed`
- `_profile` search parameter is now available. [nazrulworld]


1.0.0b3 (2018-07-30)
--------------------

- Mapping improvment for `FhirQuestionnaireResponseIndex`, `FhirObservationIndex`, `FhirProcedureRequestIndex`, `FhirTaskIndex`, `FhirDeviceRequestIndex`


1.0.0b2 (2018-07-29)
--------------------

New Features:

- supports for elasticsearch has been added. Now many basic `fhir search <https://www.hl7.org/fhir/search.html>`_ are possible to be queried.
- upto 22 FHIR fields indexes (`FhirActivityDefinitionIndex`, `FhirAppointmentIndex`, `FhirCarePlanIndex`, `FhirDeviceIndex`, `FhirDeviceRequestIndex`, `FhirHealthcareServiceIndex`, `FhirMedicationAdministrationIndex`, `FhirMedicationDispenseIndex`, `FhirMedicationRequestIndex`, `FhirMedicationStatementIndex`, `FhirObservationIndex`, `FhirOrganizationIndex`, `FhirPatientIndex`, `FhirPlanDefinitionIndex`, `FhirPractitionerIndex`, `FhirProcedureRequestIndex`, `FhirQuestionnaireIndex`, `FhirQuestionnaireResponseIndex`, `FhirRelatedPersonIndex`, `FhirTaskIndex`, `FhirValueSetIndex`)
- Mappings for all available fhir indexes are created.
- `elasticsearch` option is now available for setup.py

1.0.0b1 (2018-03-17)
--------------------

- first beta version has been released.


1.0.0a10 (2018-03-12)
---------------------

- fix(bug) Issue-3: `resource_type` constraint don't raise exception from validator.

1.0.0a9 (2018-03-08)
--------------------

- There is no restriction/limit over fhir resources, all available models are supported.


1.0.0a8 (2018-01-22)
--------------------

- fix(bug) Issue-: Empty string value raise json validation error #2:https://github.com/nazrulworld/plone.app.fhirfield/issues/2


1.0.0a7 (2018-01-21)
--------------------

- fix(bug) Issue-1: _RuntimeError: maximum recursion depth exceeded while calling a Python object at form view. #1:https://github.com/nazrulworld/plone.app.fhirfield/issues/1


1.0.0a6 (2018-01-14)
--------------------

- missing `HealthcareService` fhir model is added as supported model.


1.0.0a5 (2018-01-14)
--------------------

- `Person` fhir model added in whitelist.


1.0.0a4 (2018-01-14)
--------------------

- IFhirResource.model_interface field type changed to `DottedName` from `InterfaceField`.


1.0.0a3 (2017-12-22)
--------------------

- `FHIR Patch`_ support added. Now patching fhir resource is more easy to manage.
- plone.supermodel support is confirmed.[nazrulworld]
- plone.rfc822 marshaler field support.[nazrulworld]


1.0.0a2 (2017-12-10)
--------------------

- `FhirResourceWidget` is made working state. From now it is possible to adapt FhirResourceWidget` with z3c.form [nazrulworld]


1.0.0a1 (2017-12-05)
--------------------

- Initial release.
  [nazrulworld]

.. _`FHIR Patch`: https://www.hl7.org/fhir/fhirpatch.html
.. _`FHIRPath`: https://pypi.org/project/fhirpath/
.. _`collective.fhirpath`: https://pypi.org/project/collective.fhirpath/
