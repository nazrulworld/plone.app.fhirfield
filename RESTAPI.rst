.. _restapi_examples_doctest:

REST Client Examples
--------------------

Getting single resource, here we are getting Patient resource by ID.

Example(1)::

    >>> response = admin_session.get('/@fhir/Patient/19c5245f-89a8-49f8-b244-666b32adb92e')
    >>> response.status_code
    200
    <BLANKLINE>
    >>> response.json()['resourceType'] == 'Patient'
    True
    <BLANKLINE>
    >>> response = admin_session.get('/@fhir/Patient/19c5245f-fake-id')
    >>> response.status_code
    404
    <BLANKLINE>


Search Observation by Patient reference with status condition. Any observation until December 2017 and earlier than January 2017.

Example(2)::

    >>> response = admin_session.get('/@fhir/Observation?patient=Patient/19c5245f-89a8-49f8-b244-666b32adb92e&status=final&_lastUpdated=lt2017-12-31&_lastUpdated=gt2017-01-01')
    >>> response.status_code
    200
    >>> len(response.json())
    1
    <BLANKLINE>


Add FHIR Resource through REST API

Example(3)::

    >>> import os
    >>> import json
    >>> import uuid
    >>> import DateTime
    >>> import time

    >>> with open(os.path.join(FIXTURE_PATH, 'Patient.json'), 'r') as f:
    ...     fhir_json = json.load(f)

    >>> fhir_json['id'] = str(uuid.uuid4())
    >>> fhir_json['name'][0]['text'] = 'Another Patient'
    >>> response = admin_session.post('/@fhir/Patient', json=fhir_json)
    >>> response.status_code
    201
    >>> time.sleep(1)
    >>> response = admin_session.get('/@fhir/Patient?active=true')
    >>> len(response.json())
    2


Update (PATCH) FHIR Resource the Patient is currently activated, we will deactive.

Example(4)::

    >>> patch = [{'op': 'replace', 'path': '/active', 'value': False}]
    >>> response = admin_session.patch('/@fhir/Patient/19c5245f-89a8-49f8-b244-666b32adb92e', json={'patch': patch})
    >>> response.status_code
    204
    <BLANKLINE>
