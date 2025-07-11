# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # TODO: remove in master
    def _get_rate_date(self):
        # EXTENDS 'account'
        self.ensure_one()
        if self.move_id.country_code == 'CZ':
            return self.move_id.taxable_supply_date or self.move_id.date or fields.Date.context_today(self)
        return super()._get_rate_date()
