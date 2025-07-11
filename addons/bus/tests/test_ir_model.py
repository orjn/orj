# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj
from orj.tests import HttpCase


@orj.tests.tagged('-at_install', 'post_install')
class TestGetModelDefinitions(HttpCase):
    def test_access_cr(self):
        """ Checks that get_model_definitions does not return anything else than models """
        with self.assertRaises(KeyError):
            self.env['ir.model']._get_model_definitions(['res.users', 'cr'])

    def test_access_all_model_fields(self):
        """
            Check that get_model_definitions return all the models
            and their fields
        """
        model_definitions = self.env['ir.model']._get_model_definitions([
            'res.users', 'res.partner'
        ])
        # models are retrieved
        self.assertIn('res.users', model_definitions)
        self.assertIn('res.partner', model_definitions)
        # check that model fields are retrieved
        self.assertGreaterEqual(model_definitions['res.partner']["fields"].keys(), {'active', 'name', 'user_ids'})
        self.assertGreaterEqual(model_definitions['res.partner']["fields"].keys(), {'active', 'name', 'user_ids'})

    def test_relational_fields_with_missing_model(self):
        """
            Check that get_model_definitions only returns relational fields
            if the model is requested
        """
        model_definitions = self.env['ir.model']._get_model_definitions([
            'res.partner'
        ])
        # since res.country is not requested, country_id shouldn't be in
        # the model definition fields
        self.assertNotIn('country_id', model_definitions['res.partner']["fields"])

        model_definitions = self.env['ir.model']._get_model_definitions([
            'res.partner', 'res.country',
        ])
        # res.country is requested, country_id should be present on res.partner
        self.assertIn('country_id', model_definitions['res.partner']["fields"])
