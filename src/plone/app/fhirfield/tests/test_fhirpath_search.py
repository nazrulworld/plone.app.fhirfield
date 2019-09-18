# -*- coding: utf-8 -*-
# @Date    : 2018-05-20 10:26:23
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# Example standard query
# https://smilecdr.com/docs/current/tutorial_and_tour/fhir_search_queries.html
# https://github.com/FirelyTeam/RonFHIR
# All imports here
import copy
import json
import os
import time
import unittest
import uuid

from collective.elasticsearch.es import ElasticSearchCatalog
from DateTime import DateTime
from fhirpath.enums import FHIR_VERSION
from fhirpath.interfaces import IElasticsearchEngineFactory
from fhirpath.interfaces import IFhirSearch
from fhirpath.interfaces import ISearchContextFactory
from plone import api
from plone.app.fhirfield.exc import SearchQueryValidationError
from plone.app.fhirfield.testing import IS_TRAVIS  # noqa: E501
from zope.component import queryMultiAdapter

from . import FHIR_FIXTURE_PATH
from .base import BaseFunctionalTesting


__author__ = "Md Nazrul Islam (email2nazrul@gmail.com)"


class ElasticSearchFhirIndexFunctionalTest(BaseFunctionalTesting):
    """ """

    def get_es_catalog(self):
        """ """
        return ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

    def get_factory(self, resource_type, unrestricted=False):
        """ """
        factory = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )
        engine = factory(fhir_version=FHIR_VERSION.STU3)
        context = queryMultiAdapter((engine,), ISearchContextFactory)(
            resource_type, unrestricted=unrestricted
        )

        factory = queryMultiAdapter((context,), IFhirSearch)
        return factory

    def test_catalogsearch_fhir_date_param(self):
        """ """
        self.load_contents()
        # ************ FIXTURES ARE LOADED **************
        # test:1 equal to
        factory = self.get_factory("Organization")
        params = (("_lastUpdated", "2010-05-28T05:35:56+00:00"),)
        bundle = factory(params)
        # result should contains only item
        self.assertEqual(len(bundle.entry), 1)
        self.assertEqual(bundle.entry[0].resource.id, "f001")

        # test:2 not equal to
        params = (("_lastUpdated", "ne2015-05-28T05:35:56+00:00"),)
        bundle = factory(params)
        # result should contains two items
        self.assertEqual(len(bundle.entry), 2)

        # test:3 less than
        params = (("_lastUpdated", "lt" + DateTime().ISO8601()),)
        bundle = factory(params)
        # result should contains three items, all are less than current time
        self.assertEqual(bundle.total, 3)

        # test:4 less than or equal to
        params = (("_lastUpdated", "le2015-05-28T05:35:56+00:00"),)
        bundle = factory(params)
        # result should contains two items,
        # 2010-05-28T05:35:56+00:00 + 2015-05-28T05:35:56+00:00
        self.assertEqual(bundle.total, 2)

        # test:5 greater than
        params = (("_lastUpdated", "gt2015-05-28T05:35:56+00:00"),)
        bundle = factory(params)
        # result should contains only item
        self.assertEqual(len(bundle.entry), 1)
        self.assertEqual(bundle.entry[0].resource.id, "f003")

        # test:6 greater than or equal to
        params = (("_lastUpdated", "ge2015-05-28T05:35:56+00:00"),)
        bundle = factory(params)
        # result should contains only item
        self.assertEqual(len(bundle.entry), 2)
        return  # xxx: fix me at fhirpath
        # ** Issue: 21 **
        factory = self.get_factory("Task")
        # test IN/OR
        params = (("authored-on", "2017-08-05T06:16:41,ge2018-08-05T06:16:41"),)
        bundle = factory(params)
        # should be two
        self.assertEqual(len(bundle.entry), 2)

        params = (("authored-on", "2017-05-07T07:42:17,2019-08-05T06:16:41"),)
        bundle = factory(params)
        # Although 2019-08-05T06:16:41 realy does not exists but OR
        # feature should bring One
        self.assertEqual(len(bundle.entry), 1)

        params = (("authored-on", "lt2018-08-05T06:16:41,gt2017-05-07T07:42:17"),)

        bundle = factory(params)
        # Keep in mind OR feature! not and that's why expected result 3 not 1 because
        self.assertEqual(bundle.total, 3)

    def test_catalogsearch_fhir_token_param(self):
        """Testing FHIR search token type params, i.e status, active"""
        self.load_contents()

        factory = self.get_factory("Task")
        params = (("status", "ready"),)
        bundle = factory(params)

        # should be two tasks with having status ready
        self.assertEqual(bundle.total, 2)

        params = (("status:not", "ready"),)
        bundle = factory(params)

        # should be one task with having status draft
        self.assertEqual(bundle.total, 1)

        # test with combinition with lastUpdated
        params = (("status", "ready"), ("_lastUpdated", "lt2018-01-15T06:31:18+00:00"))

        bundle = factory(params)

        # should single task now
        self.assertEqual(len(bundle.entry), 1)

        # ** Test boolen valued token **
        factory = self.get_factory("Patient")
        params = (("active", "true"),)

        bundle = factory(params)

        # only one patient
        self.assertEqual(len(bundle.entry), 1)

        params = (("active", "false"),)

        bundle = factory(params)
        self.assertEqual(bundle.total, 0)

    def test_catalogsearch_fhir_reference_param(self):
        """Testing FHIR search reference type params, i.e subject, owner"""
        self.load_contents()

        factory = self.get_factory("Task")

        patient_id = "Patient/19c5245f-89a8-49f8-b244-666b32adb92e"

        params = (("owner", patient_id),)
        bundle = factory(params)

        # should be two tasks with having status ready
        self.assertEqual(len(bundle.entry), 2)

        params = (("owner", "Practitioner/619c1ac0-821d-46d9-9d40-a61f2578cadf"),)
        bundle = factory(params)
        self.assertEqual(len(bundle.entry), 1)

        params = (("patient", patient_id),)
        bundle = factory(params)

        self.assertEqual(len(bundle.entry), 3)

        # with compound query
        params = (("patient", patient_id), ("status", "draft"))
        # should be now only single
        bundle = factory(params)
        self.assertEqual(len(bundle.entry), 1)

        # Test with negetive
        params = (("owner:not", "Practitioner/fake-ac0-821d-46d9-9d40-a61f2578cadf"),)
        bundle = factory(params)
        # should get all tasks
        self.assertEqual(len(bundle.entry), 3)

        # Test with nested reference
        params = (
            ("based-on", "ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce"),
        )
        bundle = factory(params)

        # Should One HAQ sub task
        self.assertEqual(len(bundle.entry), 1)

    def test_catalogsearch__profile(self):
        """"""
        self.load_contents()
        # test:1 URI
        factory = self.get_factory("Organization", unrestricted=True)

        params = (("_profile", "http://hl7.org/fhir/Organization"),)
        bundle = factory(params)
        # result should contains two items
        self.assertEqual(len(bundle.entry), 2)

    def test_catalogsearch_missing_modifier(self):
        """ """
        self.load_contents()
        # add another patient
        self.admin_browser.open(self.portal_url + "/++add++FFPatient")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Patient"

        with open(os.path.join(FHIR_FIXTURE_PATH, "Patient.json"), "r") as f:
            data = json.load(f)
            data["id"] = "20c5245f-89a8-49f8-b244-666b32adb92e"
            data["gender"] = None
            self.admin_browser.getControl(
                name="form.widgets.patient_resource"
            ).value = json.dumps(data)

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        # Let's test
        factory = self.get_factory("Patient", unrestricted=True)

        params = (("gender:missing", "true"), )
        bundle = factory(params)

        self.assertEqual(1, len(bundle.entry))
        self.assertIsNone(bundle.entry[0].resource.gender)

        params = (("gender:missing", "false"), )
        bundle = factory(params)
        self.assertEqual(1, len(bundle.entry))
        self.assertIsNotNone(bundle.entry[0].resource.gender)

    def offtest_issue_5(self):
        """https://github.com/nazrulworld/plone.app.fhirfield/issues/5
        FHIR search's modifier `missing` is not working for nested mapping
        """
        self.load_contents()

        # ------ Test in Complex Data Type -------------
        # Parent Task has not partOf but each child has partOf referenced to parent
        portal_catalog = api.portal.get_tool("portal_catalog")

        result = portal_catalog.unrestrictedSearchResults(
            task_resource={"part-of:missing": "false"}
        )
        # should be two
        self.assertEqual(len(result), 2)

        result = portal_catalog.unrestrictedSearchResults(
            task_resource={"part-of:missing": "true"}
        )
        # should be one (parent Task)
        self.assertEqual(len(result), 1)

    def offtest_catalogsearch_identifier(self):
        """ """
        self.load_contents()

        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier": "240365-0002"}
        )
        self.assertEqual(len(result), 1)

        # Test with system+value
        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier": "CPR|240365-0002"}
        )
        self.assertEqual(len(result), 1)

        # Test with system only with pipe sign
        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier": "UUID|"}
        )
        self.assertEqual(len(result), 1)

        # Test with value only with pipe sign
        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier": "|19c5245f-89a8-49f8-b244-666b32adb92e"}
        )
        self.assertEqual(len(result), 1)

        # Test with empty result
        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier": "CPR|19c5245f-89a8-49f8-b244-666b32adb92e"}
        )
        self.assertEqual(len(result), 0)

        # Test with text modifier
        portal_catalog = api.portal.get_tool("portal_catalog")
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={"identifier:text": "Plone Patient UUID"}
        )
        self.assertEqual(len(result), 1)

    @unittest.skipIf(IS_TRAVIS or 1, "Ignore for travis for now, fix later")
    def offtest_identifier_query_validation(self):
        """ """
        # *
        # * unrestrictedSearchResults aka es.searchResults
        # * capture all exceptions not raising
        # * instead of logging error
        # * May be good way to capture log message
        # * https://pythonhosted.org/logutils/testing.html
        # *
        # *
        self.load_contents()

        portal_catalog = api.portal.get_tool("portal_catalog")
        try:
            portal_catalog.unrestrictedSearchResults(
                patient_resource={"identifier:text": "Plone|Patient-UUID"}
            )
            raise AssertionError(
                "Code should not come here, as validation error should raise"
            )
        except SearchQueryValidationError as e:
            self.assertIn("Pipe (|) is not allowed", str(e))

        try:
            portal_catalog.unrestrictedSearchResults(
                patient_resource={"identifier": "Plone|Patient|UUID"}
            )
            raise AssertionError(
                "Code should not come here, as validation error should raise"
            )
        except SearchQueryValidationError as e:
            self.assertIn("Only single Pipe (|)", str(e))

    def offtest_catalogsearch_array_type_reference(self):
        """Search where reference inside List """
        self.load_contents()

        portal_catalog = api.portal.get_tool("portal_catalog")
        # Search with based on
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={
                "based-on": "ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce"
            }
        )
        self.assertEqual(len(result), 1)

        # Search with part-of
        # should be two sub tasks
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={"part-of": "Task/5df31190-0ed4-45ba-8b16-3c689fc2e686"}
        )
        self.assertEqual(len(result), 2)

    def offtest_elasticsearch_sorting(self):
        """Search where reference inside List """
        self.load_contents()
        portal_catalog = api.portal.get_tool("portal_catalog")

        # Test ascending order
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={"status:missing": "false"},
            portal_type="FFTask",
            _sort="_lastUpdated",
        )

        self.assertGreater(
            result[1].getObject().task_resource.meta.lastUpdated.date,
            result[0].getObject().task_resource.meta.lastUpdated.date,
        )
        self.assertGreater(
            result[2].getObject().task_resource.meta.lastUpdated.date,
            result[1].getObject().task_resource.meta.lastUpdated.date,
        )
        # Test descending order
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={"status:missing": "false"}, _sort="-_lastUpdated"
        )

        self.assertGreater(
            result[0].getObject().task_resource.meta.lastUpdated.date,
            result[1].getObject().task_resource.meta.lastUpdated.date,
        )
        self.assertGreater(
            result[1].getObject().task_resource.meta.lastUpdated.date,
            result[2].getObject().task_resource.meta.lastUpdated.date,
        )

        # Test sorting with fhir param
        result = portal_catalog.unrestrictedSearchResults(
            portal_type="FFTask", _sort="-_lastUpdated", sort_on="task_resource"
        )

        self.assertGreater(
            result[0].getObject().task_resource.meta.lastUpdated.date,
            result[1].getObject().task_resource.meta.lastUpdated.date,
        )

    def offtest_mapping_adapter_patch(self):
        """collective.elasticsearch.mapping.MappingAdapter.
        The patch provides default index settings"""
        self.convert_to_elasticsearch()
        # Let's flush
        self.es.connection.indices.flush()
        es = ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

        settings = es.connection.indices.get_settings(es.index_name)
        settings = settings[es.real_index_name]["settings"]

        self.assertEqual(settings["index"]["mapping"]["nested_fields"]["limit"], "100")

    def offtest_quantity_type_search(self):
        """Issue: https://github.com/nazrulworld/plone.app.fhirfield/issues/7"""
        self.load_contents()

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill"

        with open(os.path.join(FHIR_FIXTURE_PATH, "ChargeItem.json"), "r") as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        self.assertIn("ffchargeitem/view", self.admin_browser.url)
        # Let's flush
        self.es.connection.indices.flush()
        # Test so normal
        portal_catalog = api.portal.get_tool("portal_catalog")

        # Test ascending order
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"quantity": "5"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"quantity": "lt5.1"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        # Test with value code/unit and system
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"price-override": "gt39.99|urn:iso:std:iso:4217|EUR"},
            portal_type="FFChargeItem",
        )
        self.assertEqual(len(brains), 1)

        # Test with code/unit and system
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"price-override": "40|EUR"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        # Test Issue#21
        fhir_json_copy = copy.deepcopy(fhir_json)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["priceOverride"].update(
            {"value": 12, "unit": "USD", "code": "USD"}
        )
        fhir_json_copy["quantity"]["value"] = 3
        fhir_json_copy["factorOverride"] = 0.54

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill (USD)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        fhir_json_copy = copy.deepcopy(fhir_json)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["priceOverride"].update(
            {"value": 850, "unit": "BDT", "code": "BDT"}
        )
        fhir_json_copy["quantity"]["value"] = 8
        fhir_json_copy["factorOverride"] = 0.21

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill(BDT)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={
                "price-override": (
                    "gt39.99|urn:iso:std:iso:4217|EUR," "le850|urn:iso:std:iso:4217|BDT"
                )
            }
        )
        self.assertEqual(len(brains), 2)

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"price-override": ("ge12," "le850")}
        )
        # should be all three now
        self.assertEqual(len(brains), 3)
        # serach by only system and code
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={
                "price-override": (
                    "|urn:iso:std:iso:4217|USD,"
                    "|urn:iso:std:iso:4217|BDT,"
                    "|urn:iso:std:iso:4217|DKK"
                )
            }
        )
        # should be 2
        self.assertEqual(len(brains), 2)

        # serach by unit only
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"price-override": ("|BDT," "|DKK")}
        )
        # should be one
        self.assertEqual(len(brains), 1)

    def offtest_number_type_search(self):
        """Issue: https://github.com/nazrulworld/plone.app.fhirfield/issues/8"""
        self.load_contents()

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill"

        with open(os.path.join(FHIR_FIXTURE_PATH, "ChargeItem.json"), "r") as f:
            fhir_json_charge_item = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_charge_item)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        # Let's flush
        self.es.connection.indices.flush()
        # Test so normal
        portal_catalog = api.portal.get_tool("portal_catalog")

        # Test normal float value order
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"factor-override": "0.8"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"factor-override": "gt0.79"},
            portal_type="FFChargeItem",
        )
        self.assertEqual(len(brains), 1)

        # Test for Encounter
        self.admin_browser.open(self.portal_url + "/++add++FFEncounter")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test FFEncounter"

        with open(os.path.join(FHIR_FIXTURE_PATH, "Encounter.json"), "r") as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.encounter_resource"
        ).value = json.dumps(fhir_json)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        brains = portal_catalog.unrestrictedSearchResults(
            encounter_resource={"length": "gt139"}, portal_type="FFEncounter"
        )
        self.assertEqual(len(brains), 1)

        # Test Issue#21
        fhir_json_copy = copy.deepcopy(fhir_json_charge_item)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["priceOverride"].update(
            {"value": 12, "unit": "USD", "code": "USD"}
        )
        fhir_json_copy["quantity"]["value"] = 3
        fhir_json_copy["factorOverride"] = 0.54

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill (USD)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        fhir_json_copy = copy.deepcopy(fhir_json_charge_item)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["priceOverride"].update(
            {"value": 850, "unit": "BDT", "code": "BDT"}
        )
        fhir_json_copy["quantity"]["value"] = 8
        fhir_json_copy["factorOverride"] = 0.21

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill(BDT)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()
        # Test with multiple equal values
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"factor-override": "0.8,0.21"}
        )
        self.assertEqual(len(brains), 2)

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"factor-override": "gt0.8,lt0.54"}
        )
        self.assertEqual(len(brains), 1)

    def offtest_issue_12(self):
        """Issue: https://github.com/nazrulworld/plone.app.fhirfield/issues/12"""
        self.load_contents()

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill"

        with open(os.path.join(FHIR_FIXTURE_PATH, "ChargeItem.json"), "r") as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        # Test code (Coding)
        portal_catalog = api.portal.get_tool("portal_catalog")

        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code": "F01510"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        # Test with system+code
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code": "http://snomed.info/sct|F01510"},
            portal_type="FFChargeItem",
        )
        self.assertEqual(len(brains), 1)

        # test with code only
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code": "|F01510"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        # test with system only
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code": "http://snomed.info/sct|"},
            portal_type="FFChargeItem",
        )
        self.assertEqual(len(brains), 1)

        # test with text
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code:text": "Nice Code"}, portal_type="FFChargeItem"
        )
        self.assertEqual(len(brains), 1)

        # test with .as(
        self.admin_browser.open(self.portal_url + "/++add++FFMedicationRequest")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill"

        with open(os.path.join(FHIR_FIXTURE_PATH, "MedicationRequest.json"), "r") as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.medicationrequest_resource"
        ).value = json.dumps(fhir_json)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        # test with only code
        brains = portal_catalog.unrestrictedSearchResults(
            medicationrequest_resource={"code": "322254008"},
            portal_type="FFMedicationRequest",
        )
        self.assertEqual(len(brains), 1)
        # test with system and code
        brains = portal_catalog.unrestrictedSearchResults(
            medicationrequest_resource={"code": "http://snomed.info/sct|"},
            portal_type="FFMedicationRequest",
        )
        self.assertEqual(len(brains), 1)

    def offtest_issue_13_address_telecom(self):
        """https://github.com/nazrulworld/plone.app.fhirfield/issues/13"""
        self.load_contents()

        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"email": "demo1@example.com"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

        # Test address with multiple paths and value for city
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"address": "Indianapolis"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

        # Test address with multiple paths and value for postCode
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"address": "46240"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

        # Test with single path for state
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"address-state": "IN"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

    def offtest_issue_15_address_telecom(self):
        """https://github.com/nazrulworld/plone.app.fhirfield/issues/15"""
        self.load_contents()

        # test with family name
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"family": "Saint"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

        # test with given name (array)
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"given": "Eelector"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

        # test with full name represent as text
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            patient_resource={"name": "Patient Saint"}, portal_type="FFPatient"
        )

        self.assertEqual(len(brains), 1)

    def offtest_issue_10(self):
        """Composite type param:
        https://github.com/nazrulworld/plone.app.fhirfield/issues/10"""
        self.load_contents()

        self.admin_browser.open(self.portal_url + "/++add++FFObservation")

        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Carbon dioxide in blood"

        with open(os.path.join(FHIR_FIXTURE_PATH, "Observation.json"), "r") as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(
            name="form.widgets.observation_resource"
        ).value = json.dumps(fhir_json)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # take a tiny snap
        time.sleep(1)
        portal_catalog = api.portal.get_tool("portal_catalog")

        # Test simple composite
        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={
                "code-value-quantity": "http://loinc.org|11557-6&6.2"
            },
            portal_type="FFObservation",
        )
        self.assertEqual(len(brains), 1)

        # Test complex composite
        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={
                "code-value-quantity": (
                    "http://loinc.org|11557-6&lt7.0," "http://kbc.org|11557-6&gt6.1"
                )
            },
            portal_type="FFObservation",
        )
        self.assertEqual(len(brains), 1)

    def offtest_issue_17(self):
        """Support for duplicate param name/value
        https://github.com/nazrulworld/plone.app.fhirfield/issues/17"""
        self.load_contents()
        portal_catalog = api.portal.get_tool("portal_catalog")
        query = {
            "task_resource": [
                ("_lastUpdated", "gt2015-10-15T06:31:18+00:00"),
                ("_lastUpdated", "lt2018-01-15T06:31:18+00:00"),
            ]
        }
        brains = portal_catalog.unrestrictedSearchResults(**query)

        self.assertEqual(len(brains), 1)

    def offtest_issue_21(self):
        """Add Support for IN/OR query for token and other if possible search type
        https://github.com/nazrulworld/plone.app.fhirfield/issues/21"""
        self.load_contents()
        new_id = str(uuid.uuid4())
        new_patient_id = str(uuid.uuid4())
        new_procedure_request_id = str(uuid.uuid4())
        self.admin_browser.open(self.portal_url + "/++add++FFTask")

        with open(os.path.join(FHIR_FIXTURE_PATH, "SubTask_HAQ.json"), "r") as f:
            json_value = json.load(f)
            json_value["id"] = new_id
            json_value["status"] = "completed"
            json_value["for"]["reference"] = "Patient/" + new_patient_id
            json_value["basedOn"][0]["reference"] = (
                "ProcedureRequest/" + new_procedure_request_id
            )

            self.admin_browser.getControl(
                name="form.widgets.task_resource"
            ).value = json.dumps(json_value)

            self.admin_browser.getControl(
                name="form.widgets.IBasic.title"
            ).value = json_value["description"]

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        # Let's flush
        self.es.connection.indices.flush()

        portal_catalog = api.portal.get_tool("portal_catalog")
        query = {"task_resource": {"status": "ready,draft"}}
        brains = portal_catalog.unrestrictedSearchResults(**query)
        # should All three tasks
        self.assertEqual(len(brains), 3)

        query = {
            "task_resource": {
                "patient": "Patient/19c5245f-89a8-49f8-b244-666b32adb92e,Patient/"
                + new_patient_id
            }
        }
        brains = portal_catalog.unrestrictedSearchResults(**query)
        # should All three tasks + one
        self.assertEqual(len(brains), 4)

        query = {
            "task_resource": {
                "based-on": (
                    "ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce,"
                    "ProcedureRequest/" + new_procedure_request_id
                )
            }
        }
        brains = portal_catalog.unrestrictedSearchResults(**query)
        # should two tasks
        self.assertEqual(len(brains), 2)

    def offtest_issue_21_code_and_coding(self):
        """Add Support for IN/OR query for token and other if possible search type
        https://github.com/nazrulworld/plone.app.fhirfield/issues/21"""
        self.load_contents()
        with open(os.path.join(FHIR_FIXTURE_PATH, "ChargeItem.json"), "r") as f:
            fhir_json = json.load(f)

        fhir_json_copy = copy.deepcopy(fhir_json)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["code"]["coding"] = [
            {
                "code": "387517004",
                "display": "Paracetamol",
                "system": "http://snomed.info/387517004",
            }
        ]
        fhir_json_copy["code"]["text"] = "Paracetamol (substance)"

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill (USD)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        fhir_json_copy = copy.deepcopy(fhir_json)
        fhir_json_copy["id"] = str(uuid.uuid4())
        fhir_json_copy["code"]["coding"] = [
            {
                "code": "387137007",
                "display": "Omeprazole",
                "system": "http://snomed.info/387137007",
            }
        ]
        fhir_json_copy["code"]["text"] = "Omeprazole (substance)"

        self.admin_browser.open(self.portal_url + "/++add++FFChargeItem")
        self.admin_browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "Test Clinical Bill(BDT)"
        self.admin_browser.getControl(
            name="form.widgets.chargeitem_resource"
        ).value = json.dumps(fhir_json_copy)
        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        # Let's flush
        self.es.connection.indices.flush()

        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={"code": "387517004,387137007"}
        )
        self.assertEqual(len(brains), 2)

        # Test with system+code with negetive
        brains = portal_catalog.unrestrictedSearchResults(
            chargeitem_resource={
                "code:not": (
                    "http://snomed.info/sct|F01510,"
                    "http://snomed.info/387137007|387137007"
                )
            }
        )
        self.assertEqual(len(brains), 1)

    def offtest_issue14_path_analizer(self):
        """ """
        self.load_contents()
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog.unrestrictedSearchResults(
            task_resource={"patient": "Patient"}
        )
        # Should Get All Tasks
        self.assertEqual(len(brains), 3)

        self.admin_browser.open(self.portal_url + "/++add++FFObservation")
        with open(os.path.join(FHIR_FIXTURE_PATH, "Observation.json"), "r") as f:
            json_value1 = json.load(f)
            self.admin_browser.getControl(
                name="form.widgets.observation_resource"
            ).value = json.dumps(json_value1)

            self.admin_browser.getControl(name="form.widgets.IBasic.title").value = (
                json_value1["resourceType"] + json_value1["id"]
            )

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)

        device_id = str(uuid.uuid4())
        self.admin_browser.open(self.portal_url + "/++add++FFObservation")
        with open(os.path.join(FHIR_FIXTURE_PATH, "Observation.json"), "r") as f:
            json_value = json.load(f)
            json_value["id"] = str(uuid.uuid4())
            json_value["subject"] = {"reference": "Device/" + device_id}
            self.admin_browser.getControl(
                name="form.widgets.observation_resource"
            ).value = json.dumps(json_value)

            self.admin_browser.getControl(name="form.widgets.IBasic.title").value = (
                json_value["resourceType"] + json_value["id"]
            )

        self.admin_browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", self.admin_browser.contents)
        self.es.connection.indices.flush()

        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={"subject": "Device"}
        )
        # Should One
        self.assertEqual(len(brains), 1)

        # Little bit complex
        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={"subject": "Device,Patient"}
        )
        self.assertEqual(len(brains), 2)

        # Search By Multiple Ids
        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={
                "subject": device_id + "," + json_value1["subject"]["reference"]
            }
        )
        self.assertEqual(len(brains), 2)

        brains = portal_catalog.unrestrictedSearchResults(
            observation_resource={"subject": device_id}
        )
        self.assertEqual(len(brains), 1)
