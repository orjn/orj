# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    lc_journal_id = fields.Many2one('account.journal')
