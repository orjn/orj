# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResPartnerActivation(models.Model):
    _name = 'res.partner.activation'
    _order = 'sequence'
    _description = 'Partner Activation'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
