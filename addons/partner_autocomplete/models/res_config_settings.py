# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_autocomplete_insufficient_credit = fields.Boolean('Insufficient credit', compute="_compute_partner_autocomplete_insufficient_credit")

    def _compute_partner_autocomplete_insufficient_credit(self):
        self.partner_autocomplete_insufficient_credit = self.env['iap.account'].get_credits('partner_autocomplete') <= 0

    def redirect_to_buy_autocomplete_credit(self):
        Account = self.env['iap.account']
        return {
            'type': 'ir.actions.act_url',
            'url': Account.get_credits_url('partner_autocomplete'),
            'target': '_new',
        }
