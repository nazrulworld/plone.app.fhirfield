Changelog
=========

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