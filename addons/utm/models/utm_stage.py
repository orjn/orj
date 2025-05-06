# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


from orj import fields, models


class UtmStage(models.Model):
    """Stage for utm campaigns."""

    _name = 'utm.stage'
    _description = 'Campaign Stage'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=1)
