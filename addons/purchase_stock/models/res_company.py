# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    days_to_purchase = fields.Float(
        string='Days to Purchase',
        help="Days needed to confirm a PO, define when a PO should be validated")
