# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, _


class HrHolidaysCancelLeave(models.TransientModel):
    _name = 'hr.holidays.cancel.leave'
    _description = 'Cancel Time Off Wizard'

    leave_id = fields.Many2one('hr.leave', string="Time Off Request", required=True)
    reason = fields.Text(required=True)

    def action_cancel_leave(self):
        self.ensure_one()

        self.leave_id._action_user_cancel(self.reason)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Your time off has been cancelled."),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
