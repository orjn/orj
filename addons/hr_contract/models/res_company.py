# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    contract_expiration_notice_period = fields.Integer("Contract Expiry Notice Period", default=7)
    work_permit_expiration_notice_period = fields.Integer("Work Permit Expiry Notice Period", default=60)
