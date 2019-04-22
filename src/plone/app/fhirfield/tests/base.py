# _*_ coding: utf-8 _*_
from collective.elasticsearch import hook
from collective.elasticsearch.es import ElasticSearchCatalog
from collective.elasticsearch.interfaces import IElasticSettings
from plone import api
from plone.app.fhirfield.testing import IS_TRAVIS  # noqa: E501
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from zope.component import getUtility

import logging
import sys
import transaction
import unittest


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
