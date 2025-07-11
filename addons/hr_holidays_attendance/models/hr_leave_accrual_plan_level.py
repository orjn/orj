# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class AccrualPlanLevel(models.Model):
    _inherit = "hr.leave.accrual.level"

    frequency_hourly_source = fields.Selection(
        selection=[
            ('calendar', 'Calendar'),
            ('attendance', 'Attendances')
        ],
        default='calendar',
        compute='_compute_frequency_hourly_source',
        store=True,
        readonly=False,
        help='If the source is set to "Calendar", the amount of worked hours will be computed based '
        "on the Employee's working schedule. Otherwise, the amount of worked hours will be based "
        'on Attendance records.')

    @api.depends('accrued_gain_time')
    def _compute_frequency_hourly_source(self):
        for level in self:
            if level.accrued_gain_time == 'start':
                level.frequency_hourly_source = 'calendar'
