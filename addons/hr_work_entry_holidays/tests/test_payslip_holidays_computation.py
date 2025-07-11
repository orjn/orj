# # -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date

from orj.addons.hr_work_entry_holidays.tests.common import TestWorkEntryHolidaysBase


class TestPayslipHolidaysComputation(TestWorkEntryHolidaysBase):

    def test_work_data(self):
        leave = self.create_leave(datetime(2015, 11, 8, 8, 0), datetime(2015, 11, 10, 22, 0), name="Doctor Appointment", employee_id=self.jules_emp.id)
        leave.action_approve()

        work_entries = self.jules_emp.contract_ids.generate_work_entries(date(2015, 11, 10), date(2015, 11, 21))
        work_entries.action_validate()
        work_entries = work_entries.filtered(lambda we: we.work_entry_type_id in self.env.ref('hr_work_entry.work_entry_type_attendance'))
        sum_hours = sum(work_entries.mapped('duration'))
        self.assertEqual(sum_hours, 59, 'It should count 59 attendance hours')  # 24h first contract + 35h second contract
