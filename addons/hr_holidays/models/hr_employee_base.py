# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timezone, timedelta
from dateutil.relativedelta import relativedelta

from orj import api, fields, models, _
from orj.exceptions import UserError, ValidationError
from orj.tools.float_utils import float_round

from orj.addons.resource.models.utils import HOURS_PER_DAY


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    leave_manager_id = fields.Many2one(
        'res.users', string='Time Off',
        compute='_compute_leave_manager', store=True, readonly=False,
        domain="[('share', '=', False), ('company_ids', 'in', company_id)]",
        help='Select the user responsible for approving "Time Off" of this employee.\n'
             'If empty, the approval is done by an Administrator or Approver (determined in settings/users).')
    remaining_leaves = fields.Float(
        compute='_compute_remaining_leaves', string='Available Time Off Days',
        help='Total number of paid time off allocated to this employee, change this value to create allocation/time off request. '
             'Total based on all the time off types without overriding limit.')
    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Time Off Status",
        selection=[
            ('confirm', 'Waiting Approval'),
            ('refuse', 'Refused'),
            ('validate1', 'Waiting Second Approval'),
            ('validate', 'Approved'),
            ('cancel', 'Cancelled')
        ])
    leave_date_from = fields.Date('From Date', compute='_compute_leave_status')
    leave_date_to = fields.Date('To Date', compute='_compute_leave_status')
    leaves_count = fields.Float('Number of Time Off', compute='_compute_remaining_leaves')
    allocation_count = fields.Float('Total number of days allocated.', compute='_compute_allocation_count')
    allocations_count = fields.Integer('Total number of allocations', compute="_compute_allocation_count")
    show_leaves = fields.Boolean('Able to see Remaining Time Off', compute='_compute_show_leaves')
    is_absent = fields.Boolean('Absent Today', compute='_compute_leave_status', search='_search_absent_employee')
    allocation_display = fields.Char(compute='_compute_allocation_remaining_display')
    allocation_remaining_display = fields.Char(compute='_compute_allocation_remaining_display')
    hr_icon_display = fields.Selection(selection_add=[
        ('presence_holiday_absent', 'On leave'),
        ('presence_holiday_present', 'Present but on leave')])

    def _compute_presence_state(self):
        super()._compute_presence_state()
        employees = self.filtered(lambda employee: employee.hr_presence_state != 'present' and employee.is_absent)
        employees.update({'hr_presence_state': 'absent'})

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days,
                        state, employee_id
                    FROM hr_leave_allocation
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                        state, employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true AND h.state='validate' AND
                s.requires_allocation='yes' AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return {row['employee_id']: row['days'] for row in self._cr.dictfetchall()}

    def _compute_remaining_leaves(self):
        remaining = {}
        if self.ids:
            remaining = self._get_remaining_leaves()
        for employee in self:
            value = float_round(remaining.get(employee.id, 0.0), precision_digits=2)
            employee.leaves_count = value
            employee.remaining_leaves = value

    def _compute_allocation_count(self):
        # Don't get allocations that are expired
        current_date = date.today()
        data = self.env['hr.leave.allocation']._read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.active', '=', True),
            ('holiday_status_id.requires_allocation', '=', 'yes'),
            ('state', '=', 'validate'),
            ('date_from', '<=', current_date),
            '|',
            ('date_to', '=', False),
            ('date_to', '>=', current_date),
        ], ['employee_id'], ['__count', 'number_of_days:sum'])
        rg_results = {employee.id: (count, days) for employee, count, days in data}
        for employee in self:
            count, days = rg_results.get(employee.id, (0, 0))
            employee.allocation_count = float_round(days, precision_digits=2)
            employee.allocations_count = count

    def _compute_allocation_remaining_display(self):
        current_date = date.today()
        allocations = self.env['hr.leave.allocation'].search([('employee_id', 'in', self.ids)])
        leaves_taken = self._get_consumed_leaves(allocations.holiday_status_id)[0]
        for employee in self:
            employee_remaining_leaves = 0
            employee_max_leaves = 0
            for leave_type in leaves_taken[employee]:
                if leave_type.requires_allocation == 'no' or not leave_type.show_on_dashboard:
                    continue
                for allocation in leaves_taken[employee][leave_type]:
                    if allocation and allocation.date_from <= current_date\
                            and (not allocation.date_to or allocation.date_to >= current_date):
                        virtual_remaining_leaves = leaves_taken[employee][leave_type][allocation]['virtual_remaining_leaves']
                        employee_remaining_leaves += virtual_remaining_leaves\
                            if leave_type.request_unit in ['day', 'half_day']\
                            else virtual_remaining_leaves / (employee.resource_calendar_id.hours_per_day or HOURS_PER_DAY)
                        employee_max_leaves += allocation.number_of_days
            employee.allocation_remaining_display = "%g" % float_round(employee_remaining_leaves, precision_digits=2)
            employee.allocation_display = "%g" % float_round(employee_max_leaves, precision_digits=2)

    def _compute_presence_icon(self):
        super()._compute_presence_icon()
        employees_absent = self.filtered(
            lambda employee: employee.hr_presence_state != 'present' and employee.is_absent)
        employees_absent.update({'hr_icon_display': 'presence_holiday_absent', 'show_hr_icon_display': True})
        employees_present = self.filtered(
            lambda employee: employee.hr_presence_state == 'present' and employee.is_absent)
        employees_present.update({'hr_icon_display': 'presence_holiday_present', 'show_hr_icon_display': True})

    def _get_first_working_interval(self, dt):
        # find the first working interval after a given date
        dt = dt.replace(tzinfo=timezone.utc)
        lookahead_days = [7, 30, 90, 180, 365, 730]
        work_intervals = None
        for lookahead_day in lookahead_days:
            periods = self._get_calendar_periods(dt, dt + timedelta(days=lookahead_day))
            if not periods:
                calendar = self.resource_calendar_id or self.company_id.resource_calendar_id
                work_intervals = calendar._work_intervals_batch(
                    dt, dt + timedelta(days=lookahead_day), resources=self.resource_id)
            else:
                for period in periods[self]:
                    start, end, calendar = period
                    work_intervals = calendar._work_intervals_batch(
                        start, end, resources=self.resource_id)
            if work_intervals.get(self.resource_id.id) and work_intervals[self.resource_id.id]._items:
                # return start time of the earliest interval
                return work_intervals[self.resource_id.id]._items[0][0]

    def _compute_leave_status(self):
        # Used SUPERUSER_ID to forcefully get status of other user's leave, to bypass record rule
        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', 'in', self.ids),
            ('date_from', '<=', fields.Datetime.now()),
            ('date_to', '>=', fields.Datetime.now()),
            ('state', '=', 'validate'),
        ])
        leave_data = {}
        for holiday in holidays:
            leave_data[holiday.employee_id.id] = {}
            leave_data[holiday.employee_id.id]['leave_date_from'] = holiday.date_from.date()
            back_on = holiday.employee_id._get_first_working_interval(holiday.date_to)
            leave_data[holiday.employee_id.id]['leave_date_to'] = back_on.date() if back_on else None
            leave_data[holiday.employee_id.id]['current_leave_state'] = holiday.state

        for employee in self:
            employee.leave_date_from = leave_data.get(employee.id, {}).get('leave_date_from')
            employee.leave_date_to = leave_data.get(employee.id, {}).get('leave_date_to')
            employee.current_leave_state = leave_data.get(employee.id, {}).get('current_leave_state')
            employee.is_absent = leave_data.get(employee.id) and leave_data.get(employee.id).get('current_leave_state') == 'validate'

    @api.depends('parent_id')
    def _compute_leave_manager(self):
        for employee in self:
            previous_manager = employee._origin.parent_id.user_id
            manager = employee.parent_id.user_id
            if manager and employee.leave_manager_id == previous_manager or not employee.leave_manager_id:
                employee.leave_manager_id = manager
            elif not employee.leave_manager_id:
                employee.leave_manager_id = False

    def _compute_show_leaves(self):
        show_leaves = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        for employee in self:
            if show_leaves or employee.user_id == self.env.user:
                employee.show_leaves = True
            else:
                employee.show_leaves = False

    def _search_absent_employee(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))
        # This search is only used for the 'Absent Today' filter however
        # this only returns employees that are absent right now.
        today_date = datetime.now(timezone.utc).date()
        today_start = fields.Datetime.to_string(today_date)
        today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', '!=', False),
            ('state', '=', 'validate'),
            ('date_from', '<=', today_end),
            ('date_to', '>=', today_start),
        ])
        operator = ['in', 'not in'][(operator == '=') != value]
        return [('id', operator, holidays.mapped('employee_id').ids)]

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('salary_simulation'):
            return super().create(vals_list)
        approver_group = self.env.ref('hr_holidays.group_hr_holidays_responsible', raise_if_not_found=False)
        group_updates = []
        for vals in vals_list:
            if 'parent_id' in vals:
                manager = self.env['hr.employee'].browse(vals['parent_id']).user_id
                vals['leave_manager_id'] = vals.get('leave_manager_id', manager.id)
            if approver_group and vals.get('leave_manager_id'):
                group_updates.append((4, vals['leave_manager_id']))
        if group_updates:
            approver_group.sudo().write({'users': group_updates})
        return super().create(vals_list)

    def write(self, values):
        if 'parent_id' in values:
            manager = self.env['hr.employee'].browse(values['parent_id']).user_id
            if manager:
                to_change = self.filtered(lambda e: e.leave_manager_id == e.parent_id.user_id or not e.leave_manager_id)
                to_change.write({'leave_manager_id': values.get('leave_manager_id', manager.id)})

        old_managers = self.env['res.users']
        if 'leave_manager_id' in values:
            old_managers = self.mapped('leave_manager_id')
            if values['leave_manager_id']:
                leave_manager = self.env['res.users'].browse(values['leave_manager_id'])
                old_managers -= leave_manager
                approver_group = self.env.ref('hr_holidays.group_hr_holidays_responsible', raise_if_not_found=False)
                if approver_group and not leave_manager.has_group('hr_holidays.group_hr_holidays_responsible'):
                    leave_manager.sudo().write({'groups_id': [(4, approver_group.id)]})

        res = super().write(values)
        # remove users from the Responsible group if they are no longer leave managers
        old_managers.sudo()._clean_leave_responsible_users()

        # Change the resource calendar of the employee's leaves in the future
        # Other modules can disable this behavior by setting the context key
        # 'no_leave_resource_calendar_update'
        if 'resource_calendar_id' in values and not self.env.context.get('no_leave_resource_calendar_update'):
            try:
                self.env['hr.leave'].search([
                    ('employee_id', 'in', self.ids),
                    ('resource_calendar_id', '!=', int(values['resource_calendar_id'])),
                    ('date_from', '>', fields.Datetime.now())]).write({'resource_calendar_id': values['resource_calendar_id']})
            except ValidationError:
                raise ValidationError(_("Changing this working schedule results in the affected employee(s) not having enough "
                                        "leaves allocated to accomodate for their leaves already taken in the future. Please "
                                        "review this employee's leaves and adjust their allocation accordingly."))

        if 'parent_id' in values or 'department_id' in values:
            today_date = fields.Datetime.now()
            hr_vals = {}
            if values.get('parent_id') is not None:
                hr_vals['manager_id'] = values['parent_id']
            if values.get('department_id') is not None:
                hr_vals['department_id'] = values['department_id']
            holidays = self.env['hr.leave'].sudo().search([
                '|',
                ('state', '=', 'confirm'),
                ('date_from', '>', today_date),
                ('employee_id', 'in', self.ids),
            ])
            holidays.write(hr_vals)
            allocations = self.env['hr.leave.allocation'].sudo().search([
                ('state', 'in', ['draft', 'confirm']),
                ('employee_id', 'in', self.ids),
            ])
            allocations.write(hr_vals)
        return res
