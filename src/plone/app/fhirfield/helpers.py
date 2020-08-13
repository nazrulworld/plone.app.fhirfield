# _*_ coding: utf-8 _*_

from urllib.parse import unquote_plus


def parse_query_string(request, allow_none=False):
    """We are not using self.request.form (parsed by Zope Publisher)!!
    There is special meaning for colon(:) in key field. For example
    `field_name:list` treats data as List and it doesn't recognize
    FHIR search modifier like :not, :missing
    as a result, from colon(:) all chars are ommited.

    Another important reason, FHIR search supports duplicate keys
    (defferent values) in query string.

    Build Duplicate Key Query String ::
        >>> import requests
        >>> params = {'patient': 'P001', 'lastUpdated': ['2018-01-01', 'lt2018-09-10']}
        >>> requests.get(url, params=params)
        >>> REQUEST['QUERY_STRING']
        'patient=P001&lastUpdated=2018-01-01&lastUpdated=lt2018-09-10'

        >>> from urllib.parse import urlencode
        >>> params = [('patient', 'P001'), ('lastUpdated', '2018-01-01'),
                      ('lastUpdated', 'lt2018-09-10')]
        >>> urlencode(params)
        'patient=P001&lastUpdated=2018-01-01&lastUpdated=lt2018-09-10'


    param:request
    param:allow_none
    """
    query_string = request.get("QUERY_STRING", "")

    if not query_string:
        return list()
    params = list()

    for q in query_string.split("&"):
        parts = q.split("=")
        param_name = unquote_plus(parts[0])
        try:
            value = parts[1] and unquote_plus(parts[1]) or None
        except IndexError:
            if not allow_none:
                continue
            value = None

        params.append((param_name, value))

    return params
