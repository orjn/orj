# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, fields


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    type = fields.Selection(selection_add=[('coupon', 'Coupon')], ondelete={'coupon': 'set default'})
