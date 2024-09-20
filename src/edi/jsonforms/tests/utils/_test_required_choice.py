# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import json

from edi.jsonforms.views.common import create_id


"""
requirements:
    * TestClass that calls the test_required_choice() function needs a self.field = [] with all the fields that can be required/optional

    len(self.field) must be at least 3
"""


def _test_required(self, ref_required):
    computed_schema = {'required': json.loads(self.view())['required']}
    ref_schema = {'required': ref_required}
    self.assertEqual(dict(computed_schema), dict(ref_schema))

def test_zero_required_choice(self):
    ref_required = []
    _test_required(self, ref_required)

def test_one_required_choice(self):
    self.field[0].required_choice = "required"
    ref_required = [create_id(self.field[0])]
    _test_required(self, ref_required)

    self.field[0].required_choice = "optional"
    self.field[1].required_choice = "required"
    ref_required = [create_id(self.field[1])]
    _test_required(self, ref_required)

    self.field[1].required_choice = "optional"
    self.field[2].required_choice = "required"
    ref_required = [create_id(self.field[2])]

    _test_required(self, ref_required)

def test_two_required_choice(self):
    id_0 = create_id(self.field[0])
    id_1 = create_id(self.field[1])
    id_2 = create_id(self.field[2])

    self.field[0].required_choice = "required"
    self.field[1].required_choice = "required"
    ref_required = [id_0, id_1]
    _test_required(self, ref_required)

    self.field[0].required_choice = "optional"
    self.field[1].required_choice = "required"
    self.field[2].required_choice = "required"
    ref_required = [id_1, id_2]
    _test_required(self, ref_required)

    self.field[1].required_choice = "optional"
    self.field[2].required_choice = "required"
    self.field[0].required_choice = "required"
    ref_required = [id_0, id_2]
    _test_required(self, ref_required)

def test_three_required_choice(self):
    self.field[0].required_choice = "required"
    self.field[1].required_choice = "required"
    self.field[2].required_choice = "required"
    ref_required = [create_id(self.field[0]), create_id(self.field[1]), create_id(self.field[2])]
    _test_required(self, ref_required)

def test_required_choices(self):
    for f in self.field:
        f.required_choice = "optional"
    test_zero_required_choice(self)
    test_one_required_choice(self)
    for f in self.field:
        f.required_choice = "optional"
    test_two_required_choice(self)
    for f in self.field:
        f.required_choice = "optional"
    test_three_required_choice(self)
