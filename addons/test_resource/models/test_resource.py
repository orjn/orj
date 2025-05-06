# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResourceTest(models.Model):
    _description = 'Test Resource Model'
    _name = 'resource.test'
    _inherit = ['resource.mixin']

    name = fields.Char()
