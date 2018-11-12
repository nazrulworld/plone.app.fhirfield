.. _restapi_examples:

RESTfull API Service
====================

Server Side codex examples
--------------------------

.. literalinclude:: ../../examples/fhirfield_rest/services/get.py
   :language: python
   :caption: Search aka GET Service

.. literalinclude:: ../../examples/fhirfield_rest/services/post.py
   :language: python
   :caption: FHIR Resource Add aka POST Service

.. literalinclude:: ../../examples/fhirfield_rest/services/patch.py
   :language: python
   :caption: FHIR Resource Update aka PATCH Service

.. literalinclude:: ../../examples/fhirfield_rest/services/configure.zcml
   :language: xml
   :caption: REST Service registration (configuration.zcml)

.. include:: ../../RESTAPI.rst