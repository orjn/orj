# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, _
from orj.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_fr_reference_leave_type = fields.Many2one(
        'hr.leave.type',
        string='Company Paid Time Off Type')

    def _get_fr_reference_leave_type(self):
        self.ensure_one()
        if not self.l10n_fr_reference_leave_type:
            raise ValidationError(_("You must first define a reference time off type for the company."))
        return self.l10n_fr_reference_leave_type
