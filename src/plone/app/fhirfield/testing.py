# -*- coding: utf-8 -*-
import os
import sys

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig


__author__ = "Md Nazrul Islam<email2nazrul@zitelab.dk>"

TEST_ZCML = """\
<configure
    xmlns="http://namespaces.zope.org/zope">
    <include package="fhirfield_rest.services" />
</configure>
"""
IS_TRAVIS = "TRAVIS" in os.environ


class PloneAppFhirfieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configuration_context):  # noqa: N802
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)

        import plone.restapi

        self.loadZCML(package=plone.restapi)

        import z3c.form

        self.loadZCML(package=z3c.form)

        import plone.app.z3cform

        self.loadZCML(package=plone.app.z3cform)

        import collective.elasticsearch

        self.loadZCML(package=collective.elasticsearch)

        import plone.app.fhirfield

        self.loadZCML(package=plone.app.fhirfield)
        # initialize method not calling automatically
        z2.installProduct(app, "plone.app.fhirfield")
        # Load Custom
        example_rest_path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                )
            ),
            "examples",
        )

        if example_rest_path not in sys.path[:]:
            sys.path.append(example_rest_path)

        xmlconfig.string(TEST_ZCML, context=configuration_context)

    def setUpPloneSite(self, portal):  # noqa: N802

        setRoles(portal, TEST_USER_ID, ["Manager"])

        applyProfile(portal, "plone.app.dexterity:default")
        applyProfile(portal, "plone.restapi:default")

        applyProfile(portal, "collective.elasticsearch:default")

        applyProfile(portal, "plone.app.fhirfield:default")

        # Apply Test profile
        applyProfile(portal, "plone.app.fhirfield:testing")


PLONE_APP_FHIRFIELD_FIXTURE = PloneAppFhirfieldLayer()


PLONE_APP_FHIRFIELD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE,),
    name="PloneAppFhirfieldLayer:IntegrationTesting",
)


PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE,),
    name="PloneAppFhirfieldLayer:FunctionalTesting",
)

PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneAppFhirfieldLayer:RestFunctionalTesting",
)

PLONE_APP_FHIRFIELD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_FHIRFIELD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="PloneAppFhirfieldLayer:AcceptanceTesting",
)
