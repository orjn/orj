# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[
        ('be', 'Belgium')
        ], ondelete={'be': lambda recs: recs.write({'invoice_reference_model': 'orj'})})
