# -*- coding:utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_edi_proxy_client_ids = fields.One2many('account_edi_proxy_client.user', inverse_name='company_id', context={'active_test': True})
