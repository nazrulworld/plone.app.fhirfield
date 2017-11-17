# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import plone.app.fhirfield


class PloneAppFhirfieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.app.fhirfield)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.fhirfield:default')


PLONE_APP_FHIRFIELD_FIXTURE = PloneAppFhirfieldLayer()


PLONE_APP_FHIRFIELD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE,),
    name='PloneAppFhirfieldLayer:IntegrationTesting'
)


PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_FHIRFIELD_FIXTURE,),
    name='PloneAppFhirfieldLayer:FunctionalTesting'
)


PLONE_APP_FHIRFIELD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_FHIRFIELD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PloneAppFhirfieldLayer:AcceptanceTesting'
)
