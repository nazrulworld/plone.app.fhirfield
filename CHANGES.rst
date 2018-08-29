Changelog
=========

1.0.0rc2 (2018-08-29)
---------------------

Bugfixes

- Issue 5: `https://github.com/nazrulworld/plone.app.fhirfield/issues/5<https://github.com/nazrulworld/plone.app.fhirfield/issues/5>`_

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