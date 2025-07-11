# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, timedelta
from freezegun import freeze_time

from orj import Command
from orj.tests import common
from orj.exceptions import UserError

class TestTimesheetGlobalTimeOff(common.TransactionCase):

    def setUp(self):
        super(TestTimesheetGlobalTimeOff, self).setUp()
        # Creates 1 test company and a calendar for employees that
        # work part time. Then creates an employee per calendar (one
        # for the standard calendar and one for the one we created)
        self.test_company = self.env['res.company'].create({
            'name': 'My Test Company',
        })

        attendance_ids = [
            (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
            (0, 0, {'name': 'Monday Lunch', 'dayofweek': '0', 'hour_from': 12, 'hour_to': 13, 'day_period': 'lunch'}),
            (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
            (0, 0, {'name': 'Tuesday Lunch', 'dayofweek': '1', 'hour_from': 12, 'hour_to': 13, 'day_period': 'lunch'}),
            (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
            (0, 0, {'name': 'Thursday Lunch', 'dayofweek': '3', 'hour_from': 12, 'hour_to': 13, 'day_period': 'lunch'}),
            (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
            (0, 0, {'name': 'Friday Lunch', 'dayofweek': '4', 'hour_from': 12, 'hour_to': 13, 'day_period': 'lunch'}),
            (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'})
        ]

        self.part_time_calendar, self.part_time_calendar2 = self.env['resource.calendar'].create([
            {
                'name': 'Part Time Calendar',
                'company_id': self.test_company.id,
                'hours_per_day': 6,
                'attendance_ids': attendance_ids,
            }, {
                'name': 'Night Watch',
                'company_id': self.test_company.id,
                'hours_per_day': 6,
                'attendance_ids': attendance_ids,
            }
        ])
        self.full_time_employee, self.full_time_employee_2,\
        self.part_time_employee, self.part_time_employee2 = self.env['hr.employee'].create([{
                'name': 'John Doe',
                'company_id': self.test_company.id,
                'resource_calendar_id': self.test_company.resource_calendar_id.id,
            }, {
                'name': 'John Smith',
                'company_id': self.test_company.id,
                'resource_calendar_id': self.test_company.resource_calendar_id.id,
            }, {
                'name': 'Jane Doe',
                'company_id': self.test_company.id,
                'resource_calendar_id': self.part_time_calendar.id,
            }, {
                'name': 'Jon Show',
                'company_id': self.test_company.id,
                'resource_calendar_id': self.part_time_calendar2.id,
            },
        ])

        # Create a 2nd company
        self.test_company_2 = self.env['res.company'].create({
            'name': 'My Test Company 2',
        })

    def _get_timesheets_by_employee(self, leave_task):
        timesheets_by_read_dict = self.env['account.analytic.line']._read_group([('task_id', '=', leave_task.id)], ['employee_id'], ['__count'])
        return {
            timesheet.id: count
            for timesheet, count in timesheets_by_read_dict
        }

    # This tests that timesheets are created for every employee with the same calendar
    # when a global time off is created.
    # This also tests that timesheets are deleted when global time off is deleted.
    def test_timesheet_creation_and_deletion_for_time_off(self):
        leave_start_datetime = datetime(2021, 1, 4, 7, 0, 0, 0)  # This is a monday
        leave_end_datetime = datetime(2021, 1, 8, 18, 0, 0, 0)  # This is a friday

        global_time_off = self.env['resource.calendar.leaves'].create({
            'name': 'Test',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        # 5 Timesheets should have been created for full_time_employee and full_time_employee_2
        # but none for part_time_employee
        leave_task = self.test_company.leave_timesheet_task_id

        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)
        self.assertFalse(timesheets_by_employee.get(self.part_time_employee.id, False))
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee.id), 5)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee_2.id), 5)

        # The standard calendar is for 8 hours/day from 8 to 12 and from 13 to 17.
        # So we need to check that the timesheets don't have more than 8 hours per day.
        self.assertEqual(leave_task.effective_hours, 80)

        # Now we delete the global time off. The timesheets should be deleted too.
        global_time_off.unlink()

        self.assertFalse(leave_task.timesheet_ids.ids)

    @freeze_time('2022-01-01 08:00:00')
    def test_timesheet_creation_and_deletion_on_employee_archive(self):
        """ Test the timesheets linked to the global time off in the future when the employee is archived """
        today = datetime.today()
        leave_start_datetime = today + timedelta(days=-today.weekday(), weeks=1)  # Next monday
        leave_end_datetime = leave_start_datetime + timedelta(days=5)  # Next friday

        self.env['resource.calendar.leaves'].create({
            'name': 'Test',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        # Create a global time-off in the same company (not specific a to calendar)
        # this should be added to calendar's leaves
        self.env['resource.calendar.leaves'].with_company(self.test_company).create({
            'name': 'Global leave',
            'calendar_id': False,
            'date_from': (leave_start_datetime + timedelta(weeks=1)).replace(hour=0, minute=0, second=0),
            'date_to': (leave_start_datetime + timedelta(weeks=1, days=1)).replace(hour=23, minute=59, second=59),
        })

        # Create a global time-off in another company which should not be
        # taken into account when creating/unarchiving employee
        self.env['resource.calendar.leaves'].with_company(self.test_company_2).create({
            'name': 'Global leave in another company',
            'calendar_id': False,
            # Monday in two weeks
            'date_from': (leave_start_datetime + timedelta(weeks=2)).replace(hour=0, minute=0, second=0),
            'date_to': (leave_start_datetime + timedelta(weeks=2)).replace(hour=23, minute=59, second=59),
        })

        # 7 Timesheets should have been created for full_time_employee
        timesheets_full_time_employee = self.env['account.analytic.line'].search([('employee_id', '=', self.full_time_employee.id)])
        self.assertEqual(len(timesheets_full_time_employee), 7)

        # All timesheets should have been deleted for full_time_employee when he is archived
        self.full_time_employee.active = False
        timesheets_full_time_employee = self.env['account.analytic.line'].search([('employee_id', '=', self.full_time_employee.id)])
        self.assertEqual(len(timesheets_full_time_employee), 0)

        # 7 Timesheets should have been created for full_time_employee when he is unarchived
        self.full_time_employee.active = True
        timesheets_full_time_employee = self.env['account.analytic.line'].search([('employee_id', '=', self.full_time_employee.id)])
        self.assertEqual(len(timesheets_full_time_employee), 7)

    # This tests that no timesheet are created for days when the employee is not supposed to work
    def test_no_timesheet_on_off_days(self):
        leave_start_datetime = datetime(2021, 1, 4, 7, 0, 0, 0)  # This is a monday
        leave_end_datetime = datetime(2021, 1, 8, 18, 0, 0, 0)  # This is a friday
        day_off = datetime(2021, 1, 6, 0, 0, 0)  # part_time_employee does not work on wednesday

        self.env['resource.calendar.leaves'].create({
            'name': 'Test',
            'calendar_id': self.part_time_calendar.id,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        # The total number of hours for the timesheet created should be equal to the
        # hours_per_day of the calendar
        leave_task = self.test_company.leave_timesheet_task_id
        self.assertEqual(leave_task.effective_hours, 4 * self.part_time_calendar.hours_per_day)

        # No timesheet should have been created on the day off
        timesheet = self.env['account.analytic.line'].search([('date', '=', day_off), ('task_id', '=', leave_task.id)])
        self.assertFalse(timesheet.id)

    # This tests that timesheets are created/deleted for every employee with the same calendar
    # when a global time off has a calendar_id set/remove
    def test_timesheet_creation_and_deletion_for_calendar_set_and_remove(self):
        leave_start_datetime = datetime(2021, 1, 4, 7, 0, 0, 0)  # This is a monday
        leave_end_datetime = datetime(2021, 1, 8, 18, 0, 0, 0)  # This is a friday

        global_time_off = self.env['resource.calendar.leaves'].create({
            'name': 'Test',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        # 5 Timesheets should have been created for full_time_employee and full_time_employee_2
        # but none for part_time_employee
        leave_task = self.test_company.leave_timesheet_task_id

        # Now we delete the calendar_id. The timesheets should be deleted too.
        global_time_off.calendar_id = False

        self.assertFalse(leave_task.timesheet_ids.ids)

        # Now we reset the calendar_id. The timesheets should be created and have the right value.
        global_time_off.calendar_id = self.test_company.resource_calendar_id.id

        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)
        self.assertFalse(timesheets_by_employee.get(self.part_time_employee.id, False))
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee.id), 5)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee_2.id), 5)

        # The standard calendar is for 8 hours/day from 8 to 12 and from 13 to 17.
        # So we need to check that the timesheets don't have more than 8 hours per day.
        self.assertEqual(leave_task.effective_hours, 80)

    def test_search_is_timeoff_task(self):
        """ Test the search method on is_timeoff_task
        with and without any hr.leave.type with timesheet_task_id defined"""
        leaves_types_with_task_id = self.env['hr.leave.type'].search([('timesheet_task_id', '!=', False)])
        self.env['project.task'].search([('is_timeoff_task', '!=', False)])

        leaves_types_with_task_id.write({'timesheet_task_id': False})
        self.env['project.task'].search([('is_timeoff_task', '!=', False)])

    def test_timesheet_creation_for_global_time_off_wo_calendar(self):
        leave_start_datetime = datetime(2021, 1, 4, 7, 0)  # This is a monday
        leave_end_datetime = datetime(2021, 1, 8, 18, 0)  # This is a friday

        global_time_off = self.env['resource.calendar.leaves'].with_company(self.test_company).create({
            'name': 'Test',
            'calendar_id': False,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        leave_task = self.test_company.leave_timesheet_task_id
        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)
        # 5 Timesheets for full time employees and 4 Timesheets for part time employees should have been created
        self.assertEqual(timesheets_by_employee.get(self.part_time_employee.id), 4)
        self.assertEqual(timesheets_by_employee.get(self.part_time_employee2.id), 4)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee.id), 5)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee_2.id), 5)
        # 8 hours/day for full time calendar employees and 6 hours/day for part time calendar employees.
        # So it should add to 2(full time employees)*5(leave days)*8(hours per day) + 2(part time employees)*4(leave days)*6(hours per day).
        self.assertEqual(leave_task.effective_hours, 128)


        # Now we set the calendar_id. The timesheets should be deleted from other calendars.
        global_time_off.calendar_id = self.test_company.resource_calendar_id.id
        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)

        self.assertFalse(timesheets_by_employee.get(self.part_time_employee.id, False))
        self.assertFalse(timesheets_by_employee.get(self.part_time_employee2.id, False))
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee.id), 5)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee_2.id), 5)
        self.assertEqual(leave_task.effective_hours, 80)

    def test_timesheet_creation_for_global_time_off_in_differant_company(self):
        leave_start_datetime = datetime(2021, 1, 4, 7, 0)  # This is a monday
        leave_end_datetime = datetime(2021, 1, 8, 18, 0)  # This is a friday

        new_company = self.env['res.company'].create({
            'name': 'Winterfell',
        })

        self.env['resource.calendar.leaves'].with_company(new_company).create({
            'name': 'Test',
            'calendar_id': False,
            'date_from': leave_start_datetime,
            'date_to': leave_end_datetime,
        })

        leave_task = self.test_company.leave_timesheet_task_id
        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)
        # Should no create timesheet if leave is in differant company then employees
        self.assertFalse(timesheets_by_employee.get(self.part_time_employee, False))
        self.assertFalse(timesheets_by_employee.get(self.full_time_employee, False))
        # Should not add any timsheets in other companies
        self.assertEqual(leave_task.effective_hours, 0)

    def test_timesheet_creation_for_global_time_off_wo_calendar_in_batch(self):
        self.env['resource.calendar.leaves'].with_company(self.test_company).create([{
            'name': "Easter Monday",
            'calendar_id': False,
            'date_from': datetime(2022, 4, 18, 5, 0, 0),
            'date_to': datetime(2022, 4, 18, 18, 0, 0),
            'resource_id': False,
            'time_type': "leave",
        }, {
            'name': "Ascension Day",
            'calendar_id': False,
            'date_from': datetime(2022, 4, 26, 5, 0, 0),
            'date_to': datetime(2022, 4, 26, 18, 0, 0),
        }])

        # 2 Timesheets for 2 global leaves should have been created for current companies all calendar employees
        leave_task = self.test_company.leave_timesheet_task_id
        timesheets_by_employee = self._get_timesheets_by_employee(leave_task)

        self.assertEqual(timesheets_by_employee.get(self.part_time_employee.id), 2)
        self.assertEqual(timesheets_by_employee.get(self.part_time_employee2.id), 2)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee.id), 2)
        self.assertEqual(timesheets_by_employee.get(self.full_time_employee_2.id), 2)
        # Total hours should be 2(part time employees)*6(hour per day)*2(leaves days) + 2(full time employees)*8(hour per day)*2(leaves days)
        self.assertEqual(leave_task.effective_hours, 56)

    def test_timesheet_creation_and_deletion_for_calendar_update(self):
        """
            Check that employee's timesheets are correctly updated when the employee's calendar
            is modified for public holidays after today's date.
        """
        attendance_ids_40h = [
            Command.create({'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            Command.create({'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            Command.create({'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            Command.create({'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            Command.create({'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'})
        ]
        attendance_ids_35h = [
            Command.create({'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            Command.create({'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            Command.create({'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            Command.create({'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'}),
            Command.create({'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            Command.create({'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 16, 'day_period': 'afternoon'})
        ]
        calendar_40h, calendar_35h = self.env['resource.calendar'].create([
            {
                'name': 'Calendar 40h',
                'company_id': self.test_company.id,
                'hours_per_day': 8,
                'attendance_ids': attendance_ids_40h,
            },
            {
                'name': 'Calendar 35h',
                'company_id': self.test_company.id,
                'hours_per_day': 8,
                'attendance_ids': attendance_ids_35h,
            }
        ])
        gto_09_04, gto_09_11, gto_11_06, gto_11_13 = self.env['resource.calendar.leaves'].create([
            {
                'name': 'Global Time Off 4 Setpember',
                'date_from': datetime(2023, 9, 4, 7, 0, 0, 0),
                'date_to': datetime(2023, 9, 4, 18, 0, 0, 0),
                'calendar_id': calendar_40h.id,
            },
            {
                'name': 'Global Time Off 11 Setpember',
                'date_from': datetime(2023, 9, 11, 7, 0, 0, 0),
                'date_to': datetime(2023, 9, 11, 18, 0, 0, 0),
                'calendar_id': calendar_35h.id,
            },
            {
                'name': 'Global Time Off 6 November',
                'date_from': datetime(2023, 11, 6, 7, 0, 0, 0),
                'date_to': datetime(2023, 11, 6, 18, 0, 0, 0),
                'calendar_id': calendar_40h.id,
            },
            {
                'name': 'Global Time Off 13 November',
                'date_from': datetime(2023, 11, 13, 7, 0, 0, 0),
                'date_to': datetime(2023, 11, 13, 18, 0, 0, 0),
                'calendar_id': calendar_35h.id,
            }
        ])

        with freeze_time('2023-08-10'):
            self.full_time_employee.resource_calendar_id = calendar_40h.id
        timesheets_employee_40h = self.env['account.analytic.line'].search([('employee_id', '=', self.full_time_employee.id)])
        global_leaves_ids_40h = timesheets_employee_40h.global_leave_id
        self.assertEqual(len(global_leaves_ids_40h), 2)
        self.assertIn(gto_09_04, global_leaves_ids_40h)
        self.assertIn(gto_11_06, global_leaves_ids_40h)

        with freeze_time('2023-10-10'):
            self.full_time_employee.resource_calendar_id = calendar_35h.id
        timesheets_employee_35h = self.env['account.analytic.line'].search([('employee_id', '=', self.full_time_employee.id)])
        global_leaves_ids_35h = timesheets_employee_35h.global_leave_id
        self.assertEqual(len(global_leaves_ids_35h), 2)
        self.assertIn(gto_09_04, global_leaves_ids_35h)
        self.assertIn(gto_11_13, global_leaves_ids_35h)
        self.assertNotIn(gto_09_11, global_leaves_ids_35h)

    def test_global_time_off_timesheet_creation_after_leave_refusal(self):
        """ When a global time off is created and an employee already has a
            validated leave at that date, a timesheet is not created for the
            global time off.
            We make sure that the global time off timesheet is restored if the
            leave is refused.
        """
        test_user = self.env['res.users'].with_company(self.test_company).create({
            'name': 'Jonathan Doe',
            'login': 'jdoe@example.com',
        })
        test_user.with_company(self.test_company).action_create_employee()
        test_user.employee_id.write({
            'resource_calendar_id': self.test_company.resource_calendar_id.id,
        })
        # needed for cancelled leave chatter message
        test_user.partner_id.write({
            'email': 'jdoe@example.com',
        })

        # employee leave dates: from monday to friday
        today = datetime.today()
        next_monday = today.date() + timedelta(days=-today.weekday(), weeks=1)
        hr_leave_start_datetime = datetime(next_monday.year, next_monday.month, next_monday.day, 8, 0, 0) # monday next week
        hr_leave_end_datetime = hr_leave_start_datetime + timedelta(days=4, hours=9) # friday next week

        self.env.company = self.test_company

        internal_project = self.test_company.internal_project_id
        internal_task_leaves = self.test_company.leave_timesheet_task_id

        hr_leave_type_with_ts = self.env['hr.leave.type'].create({
            'name': 'Leave Type with timesheet generation',
            'requires_allocation': 'no',
            'timesheet_generate': True,
            'timesheet_project_id': internal_project.id,
            'timesheet_task_id': internal_task_leaves.id,
        })

        # create and validate a leave for full time employee
        HrLeave = self.env['hr.leave'].with_context(mail_create_nolog=True, mail_notrack=True)
        holiday = HrLeave.with_user(test_user).create({
            'name': 'Leave 1',
            'employee_id': test_user.employee_id.id,
            'holiday_status_id': hr_leave_type_with_ts.id,
            'request_date_from': hr_leave_start_datetime,
            'request_date_to': hr_leave_end_datetime,
        })
        holiday.sudo().action_validate()
        self.assertEqual(len(holiday.timesheet_ids), 5)

        # create overlapping global time off
        global_leave_start_datetime = hr_leave_start_datetime + timedelta(days=2)
        global_leave_end_datetime = global_leave_start_datetime + timedelta(hours=9)

        global_time_off = self.env['resource.calendar.leaves'].create({
            'name': 'Public Holiday',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': global_leave_start_datetime,
            'date_to': global_leave_end_datetime,
        })
        gto_without_calendar = self.env['resource.calendar.leaves'].create({
            'name': 'Public Holiday without calendar',
            'date_from': global_leave_start_datetime + timedelta(days=1), # still within the hr.leave being refused
            'date_to': global_leave_end_datetime + timedelta(days=1),
        })

        # timesheets linked to global time offs should not exist as one already exists for the leave
        self.assertFalse(global_time_off.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))
        self.assertFalse(gto_without_calendar.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))

        # refuse original leave
        holiday.sudo().action_refuse()
        self.assertFalse(holiday.timesheet_ids)

        # timesheets linked to global time offs should be restored as the existing leave timesheets were unlinked after refusal
        self.assertTrue(global_time_off.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))
        self.assertTrue(gto_without_calendar.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))

        # remove global time offs to remove the timesheet so we can test cancelling the leave
        global_time_off.unlink()
        gto_without_calendar.unlink()

        # create a new leave at same dates
        holiday2 = HrLeave.with_user(test_user).create({
            'name': 'Leave 2',
            'employee_id': test_user.employee_id.id,
            'holiday_status_id': hr_leave_type_with_ts.id,
            'request_date_from': hr_leave_start_datetime,
            'request_date_to': hr_leave_end_datetime,
        })
        holiday2.sudo().action_validate()

        # recreate the global time off
        global_time_off = self.env['resource.calendar.leaves'].create({
            'name': 'Public Holiday',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': global_leave_start_datetime,
            'date_to': global_leave_end_datetime,
        })
        gto_without_calendar = self.env['resource.calendar.leaves'].create({
            'name': 'Public Holiday without calendar',
            'date_from': global_leave_start_datetime + timedelta(days=1), # still within the hr.leave being cancelled
            'date_to': global_leave_end_datetime + timedelta(days=1),
        })

        # timesheets linked to global time offs should not exist as one already exists for the leave
        self.assertFalse(global_time_off.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))
        self.assertFalse(gto_without_calendar.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))

        # cancel the leave
        holiday2.with_user(test_user)._action_user_cancel('User cancelled leave')
        self.assertFalse(holiday2.timesheet_ids)

        self.assertTrue(global_time_off.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))
        self.assertTrue(gto_without_calendar.timesheet_ids.filtered(lambda r: r.employee_id == test_user.employee_id))

    def test_unlink_timesheet_with_global_time_off(self):
        leave_start = datetime(2025, 1, 1, 7, 0)
        leave_end = datetime(2025, 1, 1, 18, 0)

        global_time_off = self.env['resource.calendar.leaves'].create({
            'name': 'Public Holiday',
            'calendar_id': self.test_company.resource_calendar_id.id,
            'date_from': leave_start,
            'date_to': leave_end,
        })

        timesheet = self.env['account.analytic.line'].search([
            ('global_leave_id', '=', global_time_off.id),
            ('employee_id', '=', self.full_time_employee.id)
        ])

        with self.assertRaises(UserError):
            timesheet.unlink()
