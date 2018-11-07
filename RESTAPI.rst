REST API Examples
=================


Simple Search: Getting single resource, here we are getting Patient resource by ID.
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

