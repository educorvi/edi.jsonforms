# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import edi.jsonforms


class EdiJsonformsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=edi.jsonforms)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'edi.jsonforms:default')


EDI_JSONFORMS_FIXTURE = EdiJsonformsLayer()


EDI_JSONFORMS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EDI_JSONFORMS_FIXTURE,),
    name='EdiJsonformsLayer:IntegrationTesting',
)


EDI_JSONFORMS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EDI_JSONFORMS_FIXTURE,),
    name='EdiJsonformsLayer:FunctionalTesting',
)


EDI_JSONFORMS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        EDI_JSONFORMS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='EdiJsonformsLayer:AcceptanceTesting',
)
