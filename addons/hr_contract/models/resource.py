# -*- coding:utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from orj import fields, models
from orj.osv.expression import AND


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    contracts_count = fields.Integer("# Contracts using it", compute='_compute_contracts_count', groups="hr_contract.group_hr_contract_manager")

    def transfer_leaves_to(self, other_calendar, resources=None, from_date=None):
        """
            Transfer some resource.calendar.leaves from 'self' to another calendar 'other_calendar'.
            Transfered leaves linked to `resources` (or all if `resources` is None) and starting
            after 'from_date' (or today if None).
        """
        from_date = from_date or fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        domain = [
            ('calendar_id', 'in', self.ids),
            ('date_from', '>=', from_date),
        ]
        domain = AND([domain, [('resource_id', 'in', resources.ids)]]) if resources else domain

        self.env['resource.calendar.leaves'].search(domain).write({
            'calendar_id': other_calendar.id,
        })

    def _compute_contracts_count(self):
        count_data = self.env['hr.contract']._read_group(
            [('resource_calendar_id', 'in', self.ids), ('employee_id', '!=', False)],
            ['resource_calendar_id'],
            ['__count'])
        mapped_counts = {resource_calendar.id: count for resource_calendar, count in count_data}
        for calendar in self:
            calendar.contracts_count = mapped_counts.get(calendar.id, 0)

    def action_open_contracts(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hr_contract.action_hr_contract")
        action.update({'domain': [('resource_calendar_id', '=', self.id), ('employee_id', '!=', False)]})
        return action
