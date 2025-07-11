# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import re
from orj import api, fields, models, _
from orj.exceptions import ValidationError


class PrintPreNumberedChecks(models.TransientModel):
    _name = 'print.prenumbered.checks'
    _description = 'Print Pre-numbered Checks'

    next_check_number = fields.Char('Next Check Number', required=True)

    @api.constrains('next_check_number')
    def _check_next_check_number(self):
        for check in self:
            if check.next_check_number and not re.match(r'^[0-9]+$', check.next_check_number):
                raise ValidationError(_('Next Check Number should only contains numbers.'))

    def print_checks(self):
        check_number = int(self.next_check_number)
        number_len = len(self.next_check_number or "")
        payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
        payments.filtered(lambda r: r.state == 'draft').action_post()
        payments.filtered(lambda r: r.state == 'in_process' and not r.is_sent).write({'is_sent': True})
        for payment in payments:
            payment.check_number = '%0{}d'.format(number_len) % check_number
            check_number += 1
        checks_action = payments.do_print_checks()
        checks_action.update({'close_on_report_download': True})
        return checks_action
