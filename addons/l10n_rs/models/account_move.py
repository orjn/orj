# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_rs_turnover_date = fields.Date(string='Turnover Date')
