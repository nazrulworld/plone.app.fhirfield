# -*- coding: utf-8 -*-
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING  # noqa: 501
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from plone.restapi.testing import RelativeSession
from plone.testing import layered
from plone.testing import z2
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import TestRequest

import io
import json
import os
import six
import time
import transaction
import unittest


try:  # pragma: no cover
    from zope.testrunner import doctest
except ImportError:  # pragma: no cover
    # less than version 4.2.0 use standard
    import doctest


def make_session(portal, base_url=None):
    """ """
    base_url = base_url or portal.portal_url()
    session = RelativeSession(base_url)
    session.headers.update(
        {
            "Accept-Language": "en",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    return session


def error_setup(portal, browser):
    """ """
    browser.handleErrors = False
    portal.error_log._ignored_exceptions = ()

    def raising(self, info):
        import traceback

        traceback.print_tb(info[2])
        six.print_(info[1])

    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog

    SiteErrorLog.raising = raising


def create_content_from_fhir_json(container, fhir_json):
    """ """
    body = {
        "@type": "FF" + fhir_json["resourceType"],
        "title": "{0}/{1}".format(fhir_json["resourceType"], fhir_json["id"]),
        "{0}_resource".format(fhir_json["resourceType"].lower()): fhir_json,
    }

    request = TestRequest(BODY=json.dumps(body))
    obj = create(container, body["@type"], id_=fhir_json["id"], title=body["title"])

    deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)

    notify(ObjectCreatedEvent(obj))

    deserializer(validate_all=True)

    obj = add(container, obj, False)

    return obj


def init_fixture(portal, fixture_path):
    """ """
    if not os.path.exists(fixture_path):
        raise LookupError("Path {0} doesn't exists!".format(fixture_path))
    for root, dirs, files in os.walk(fixture_path, topdown=True):

        for file_ in files:

            if not file_.endswith(".json"):
                continue

            with io.open(os.path.join(root, file_), "r", encoding="utf-8") as f:
                fhir_json = json.load(f, encoding="utf-8")
                create_content_from_fhir_json(portal, fhir_json)


def setup_ES(portal, admin_browser):
    """ """
    portal_catalog_url = getattr(portal, "portal_catalog").absolute_url()

    default_indexes = [
        "Description",
        "SearchableText",
        "Title",
        "organization_resource",
        "patient_resource",
        "questionnaire_resource",
        "questionnaireresponse_resource",
        "task_resource",
        "valueset_resource",
        "device_resource",
        "devicerequest_resource",
        "procedurerequest_resource",
        "chargeitem_resource",
        "encounter_resource",
        "medicationrequest_resource",
        "observation_resource",
        "media_resource",
    ]

    # first we making sure to transfer handler
    admin_browser.open(portal.portal_url() + "/@@elastic-controlpanel")
    admin_browser.getControl(name="form.widgets.es_only_indexes").value = "\n".join(
        default_indexes
    )
    admin_browser.getControl(name="form.widgets.enabled:list").value = [True]
    admin_browser.getControl(name="form.buttons.save").click()

    form = admin_browser.getForm(action=portal_catalog_url + "/@@elastic-convert")
    form.getControl(name="convert").click()


def setUp(doctest):
    """ """

    layer = doctest.globs["layer"]
    app = layer["app"]
    portal = layer["portal"]

    # Paths defination
    FIXTURE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixture", "FHIR"
    )

    # browser setup
    anon_browser = z2.Browser(app)
    error_setup(portal, anon_browser)

    admin_browser = z2.Browser(app)
    admin_browser.addHeader(
        "Authorization", "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    )

    error_setup(portal, admin_browser)

    # REST client initialization
    admin_session = make_session(portal)
    admin_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    anon_session = make_session(portal)

    # Setup ES
    setup_ES(portal, admin_browser)

    # Fixtures
    init_fixture(portal, FIXTURE_PATH)

    transaction.commit()

    # let's wait a bit
    time.sleep(1)

    doctest.globs.update(locals())


def test_suite():
    """ """
    suite = unittest.TestSuite()

    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    "../../../../../RESTAPI.rst",
                    setUp=setUp,
                    optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                    | doctest.NORMALIZE_WHITESPACE
                    | doctest.ELLIPSIS,
                ),
                layer=PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING,
            )
        ]
    )
    return suite
