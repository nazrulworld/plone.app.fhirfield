Changelog
=========


1.0.0a7 (unreleased)
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