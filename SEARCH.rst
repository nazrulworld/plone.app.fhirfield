FHIR SEARCH
===========

This product has a query builder helper, that is actually transforming `fhir search`_ params into `Plone's search compatible <https://docs.plone.org/develop/plone/searching_and_indexing/query.html>`_ params so that PortalCatalog tool understand what to do. Each of FHIR Indexes provided by this product, by default using this query builder but it is possible to provide prepared query.


Query Builder
-------------

``plone.app.fhir.field.helpers.build_elasticsearch_query`` takes only `HL7 fhir standard search parameters <https://www.hl7.org/fhir/searchparameter-registry.html>`_ and transforms to elasticsearch compatible query that is executing through plone catalog search. However belows are lists of standard parameters those are supported by this `Query Builder` (more to continue adding, until full supports are completed)


Integrate in your REST API service
----------------------------------

This product has been got all battery included to be integrated with plone.restapi for becoming `HL7 FHIR standard RESTful API <https://www.hl7.org/fhir/http.html#search>`_  server which would provide search service as `defined here <https://www.hl7.org/fhir/search.html>`_.

`Example RESTful service could be found here <tests/fhir_rest_service/get.py>`_


+------------------+------------------------------+---------------------------------+
| Parameter Name   | Example                      | Remarks                         |
+==================+==============================+=================================+
| `_id`            |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `_lastUpdated`   |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `_profile`       |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `birthdate`      |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `gender`         |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `patient`        |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `status`         |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `owner`          |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `subject`        |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `effective`      |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `url`            |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `version`        |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `authored`       |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `identifier`     |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `based-on`       |                              | Yes                             |
+------------------+------------------------------+---------------------------------+
| `part-of`        |                              | Yes                             |
+------------------+------------------------------+---------------------------------+

.. _`fhir search`: https://www.hl7.org/fhir/search.html
