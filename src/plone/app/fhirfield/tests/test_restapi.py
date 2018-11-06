# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING  # noqa: 501
from plone.testing import layered
from zope.testing import doctest

import os
import unittest


def make_session(portal, base_url=None):
    """ """
    base_url = base_url or portal.portal_url()
    session = RelativeSession(base_url)
    session.headers.update({
        'Accept-Language': 'en',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })
    return session


def setUp(doctest):
    """ """

    layer = doctest.globs['layer']
    app = layer['app']
    portal = layer['portal']

    # Paths defination
    FIXTURE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'FHIR')

    # REST client initialization
    admin_session = make_session(portal)
    admin_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    anon_session = make_session(portal)

    doctest.globs.update(locals())


def test_suite():
    """ """
    suite = unittest.TestSuite()

    suite.addTests([
        layered(doctest.DocFileSuite(
            '../../../../../RESTAPI.rst',
            setUp=setUp,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            layer=PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING,
        ),
    ])
    return suite
