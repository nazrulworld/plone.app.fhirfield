# _*_ coding: utf-8 _*_
import json
import logging
import os
import sys
import unittest

import transaction
from collective.elasticsearch import hook
from collective.elasticsearch.es import ElasticSearchCatalog
from collective.elasticsearch.interfaces import IElasticSettings
from DateTime import DateTime
from plone import api
from plone.app.fhirfield.testing import IS_TRAVIS  # noqa: E501
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from zope.component import getUtility

from . import FHIR_FIXTURE_PATH


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


def clearTransactionEntries(es):
    _hook = hook.getHook(es)
    _hook.remove = []
    _hook.index = {}


def tear_down_es(es):
    """ """
    es.connection.indices.delete_alias(index=es.real_index_name, name=es.index_name)
    es.connection.indices.delete(index=es.real_index_name)
    clearTransactionEntries(es)


def setup_es(self, es_only_indexes={u"Title", u"Description", u"SearchableText"}):
    """ """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IElasticSettings, check=False)  # noqa: P001
    # set host
    host = os.environ.get("ES_SERVER_HOST", "127.0.0.1")
    settings.hosts = [host]
    # disable sniffing hosts in tests because docker...
    settings.sniffer_timeout = None
    settings.enabled = True
    settings.sniffer_timeout = 0.0
    settings.es_only_indexes = es_only_indexes

    self.catalog = api.portal.get_tool("portal_catalog")
    self.catalog._elasticcustomindex = "plone-test-index"
    self.es = ElasticSearchCatalog(self.catalog)
    self.catalog.manage_catalogRebuild()


class BaseTesting(unittest.TestCase):
    """" """

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.portal_url = api.portal.get_tool("portal_url")()
        self.portal_catalog_url = api.portal.get_tool("portal_catalog").absolute_url()

        setup_es(self)
        # need to commit here so all tests start with a baseline
        # of elastic enabled
        self.commit()

    def commit(self):
        transaction.commit()

    def enable_event_log(self, loggers=None, plone_log_level="ERROR"):
        """
            :param loggers: dict of loggers. format {'logger name': 'level name'}
            :param plone_log_level: log level of plone. default is ERROR
         """
        defaults = {"plone.app.fhirfield": "INFO", "collective.elasticsearch": "DEBUG"}
        from Products.CMFPlone.log import logger

        loggers = loggers or defaults

        for logger_name, level_name in loggers.items():
            logging.getLogger(logger_name).setLevel(
                getattr(logging, level_name.upper())
            )
        # Plone log level:
        logger.root.setLevel(getattr(logging, plone_log_level.upper()))

        # Enable output when running tests:
        logger.root.addHandler(logging.StreamHandler(sys.stdout))

    def convert_to_elasticsearch(self, indexes=list()):
        """ """
        default_indexes = ["Description", "SearchableText", "Title"]
        if indexes:
            default_indexes.extend(indexes)
        # first we making sure to transfer handler
        self.admin_browser.open(self.portal_url + "/@@elastic-controlpanel")
        self.admin_browser.getControl(
            name="form.widgets.es_only_indexes"
        ).value = "\n".join(default_indexes)
        self.admin_browser.getControl(name="form.widgets.enabled:list").value = True
        self.admin_browser.getControl(name="form.buttons.save").click()

        form = self.admin_browser.getForm(
            action=self.portal_catalog_url + "/@@elastic-convert"
        )
        form.getControl(name="convert").click()
        # Let's flush
        self.es.connection.indices.flush()

    def load_contents(self):
        """ """
        self.convert_to_elasticsearch(
            [
                "organization_resource",
                "medicationrequest_resource",
                "patient_resource",
                "task_resource",
                "chargeitem_resource",
                "encounter_resource",
                "observation_resource",
            ]
        )

        self.admin_browser.open(self.portal_url + "/++add++FFOrganization")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Hospital"

        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            self.admin_browser.getControl(
                name="form.widgets.organization_resource"
            ).value = f.read()
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + "/++add++FFOrganization")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Hamid Patuary University"
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_value = json.load(f)
            json_value["id"] = "f002"
            json_value["meta"]["lastUpdated"] = "2015-05-28T05:35:56+00:00"
            json_value["meta"]["profile"] = ["http://hl7.org/fhir/Organization"]
            json_value["name"] = "Hamid Patuary University"
            self.admin_browser.getControl(
                name="form.widgets.organization_resource"
            ).value = json.dumps(json_value)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + "/++add++FFOrganization")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Call trun University"
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_value = json.load(f)
            json_value["id"] = "f003"
            json_value["meta"]["lastUpdated"] = DateTime().ISO8601()
            json_value["meta"]["profile"] = [
                "http://hl7.org/fhir/Meta",
                "urn:oid:002.160",
            ]
            json_value["name"] = "Call trun University"
            self.admin_browser.getControl(
                name="form.widgets.organization_resource"
            ).value = json.dumps(json_value)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        # add patient
        self.admin_browser.open(self.portal_url + "/++add++FFPatient")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Patient"

        with open(os.path.join(FHIR_FIXTURE_PATH, "Patient.json"), "r") as f:
            self.admin_browser.getControl(
                name="form.widgets.patient_resource"
            ).value = f.read()

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        # add tasks
        self.admin_browser.open(self.portal_url + "/++add++FFTask")
        with open(os.path.join(FHIR_FIXTURE_PATH, "ParentTask.json"), "r") as f:
            json_value = json.load(f)
            self.admin_browser.getControl(
                name="form.widgets.task_resource"
            ).value = json.dumps(json_value)

            self.admin_browser.getControl(
                name="form.widgets.IBasic.title"
            ).value = json_value["description"]

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + "/++add++FFTask")
        with open(os.path.join(FHIR_FIXTURE_PATH, "SubTask_HAQ.json"), "r") as f:
            json_value = json.load(f)
            self.admin_browser.getControl(
                name="form.widgets.task_resource"
            ).value = json.dumps(json_value)

            self.admin_browser.getControl(
                name="form.widgets.IBasic.title"
            ).value = json_value["description"]

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + "/++add++FFTask")
        with open(os.path.join(FHIR_FIXTURE_PATH, "SubTask_CRP.json"), "r") as f:
            json_value = json.load(f)
            self.admin_browser.getControl(
                name="form.widgets.task_resource"
            ).value = json.dumps(json_value)

            self.admin_browser.getControl(
                name="form.widgets.IBasic.title"
            ).value = json_value["description"]

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        # ES indexes to be ready
        # Let's flush
        self.es.connection.indices.flush()

    def tearDown(self):
        """ """
        super(BaseTesting, self).tearDown()
        tear_down_es(self.es)


class BaseFunctionalTesting(BaseTesting):
    """ """

    layer = PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        super(BaseFunctionalTesting, self).setUp()

        self.anon_browser = z2.Browser(self.layer["app"])
        self.error_setup(self.anon_browser)

        self.admin_browser = z2.Browser(self.layer["app"])
        self.admin_browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.error_setup(self.admin_browser)
        if not IS_TRAVIS and 1 == 2:
            self.enable_event_log()

    def error_setup(self, browser):
        """ """
        browser.handleErrors = False
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback

            traceback.print_tb(info[2])
            print(info[1])

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog

        SiteErrorLog.raising = raising


class BaseRestFunctionalTesting(BaseTesting):
    """ """

    layer = PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        super(BaseFunctionalTesting, self).setUp()
