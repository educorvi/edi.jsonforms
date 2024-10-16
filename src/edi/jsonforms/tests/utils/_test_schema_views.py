# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest

layer = EDI_JSONFORMS_INTEGRATION_TESTING

def setUp_integration_test(self):
    self.portal = self.layer['portal']
    setRoles(self.portal, TEST_USER_ID, ['Manager'])
    api.content.create(self.portal, 'Folder', 'other-folder')
    api.content.create(self.portal, 'Document', 'front-page')
    form = api.content.create(self.portal, 'Form', 'Fragebogen')

    fragestellung = api.content.create(type='Field', title='Fragestellung', container=form)
    self.ids[fragestellung.title] = fragestellung.id
    
    auswahlfeld = api.content.create(type='SelectionField', title='Auswahlfeld', container=form)
    self.ids[auswahlfeld.title] = auswahlfeld.id

    uploadfeld = api.content.create(type='UploadField', title='Uploadfeld', container=form)
    self.ids[uploadfeld.title] = uploadfeld.id

    array = api.content.create(type='Array', title='Array', container=form)
    self.ids[array.title] = array.id

    object = api.content.create(type='Complex', title='Object', container=form)
    self.ids[object.title] = object.id

    feldgruppe = api.content.create(type='Fieldset', title='Feldgruppe', container=form)
    self.ids[feldgruppe.title] = feldgruppe.id


def test_json_schema_view_is_registered(self, view_name):
    try:
        view = getMultiAdapter(
            (self.portal['Fragebogen'], self.portal.REQUEST), name=view_name
        )
        self.assertTrue(view.__name__ == view_name)
    except ComponentLookupError:
        self.assertTrue(1==0, msg="ComponentLookUpError should not happen when trying to apply the " + str(view_name) + " to a Form.")

def test_json_schema_view_not_matching_interface(self, view_name):
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['front-page'], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Fragestellung']], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Auswahlfeld']], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Uploadfeld']], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Array']], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Object']], self.portal.REQUEST),
            name=view_name
        )
    with self.assertRaises(ComponentLookupError):
        getMultiAdapter(
            (self.portal['Fragebogen'][self.ids['Feldgruppe']], self.portal.REQUEST),
            name=view_name
        )


# set up a test, that needs a form and a view
def setUp_json_schema_test(self):
    self.portal = self.layer['portal']
    self.request = self.layer['request']
    setRoles(self.portal, TEST_USER_ID, ['Manager'])
    self.form = api.content.create(self.portal, "Form", "Fragebogen")
    self.view = api.content.get_view(
        name="json-schema-view",
        context=self.portal['Fragebogen'],
        request=self.request,
    )
    self.maxDiff = None


def setUp_ui_schema_test(self):
    pass