# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class LunchLocation(models.Model):
    _name = 'lunch.location'
    _description = 'Lunch Locations'

    name = fields.Char('Location Name', required=True)
    address = fields.Text('Address')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
