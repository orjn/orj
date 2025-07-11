# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.crm.tests.test_crm_lead_merge import TestLeadMergeCommon
from orj.addons.event_crm.tests.common import TestEventCrmCommon
from orj.tests.common import tagged, users


@tagged('lead_manage')
class TestLeadCrmMerge(TestLeadMergeCommon, TestEventCrmCommon):

    @users('user_sales_manager')
    def test_merge_different_events_and_update(self):
        """Check that merging leads related to different events works and keeps the sync working.

        If leads are merged after being linked to registrations on different events, sync should
        still be able to pick values to set on the lead.
        """
        other_event = self.env['event.event'].sudo().create({
            'name': 'TestOtherEvent',
            'date_tz': 'Europe/Brussels',
        })
        self.test_rule_order_done.event_registration_filter = repr(
            [('name', 'like', 'test-send-email-on-leads-with-multiple-events-_')]
        )

        # create registrations and check rule generated leads
        registrations = self.env['event.registration'].sudo().create([{
            'email': self.event_customer.email,
            'event_id': self.event_0.id,
            'name': 'test-send-email-on-leads-with-multiple-events-1',
            'partner_id': False,
            'state': 'done',
        }, {
            'email': self.event_customer.email,
            'event_id': other_event.id,
            'name': 'test-send-email-on-leads-with-multiple-events-2',
            'partner_id': False,
            'state': 'done',
        }])
        self.assertTrue(registrations[0].lead_ids, "Order rule should have created leads for both registrations")
        self.assertTrue(registrations[1].lead_ids, "Order rule should have created leads for both registrations")
        self.assertFalse(
            registrations[0].lead_ids & registrations[1].lead_ids,
            "Different events should create different leads"
        )
        self.assertFalse(
            registrations.lead_ids.partner_id,
            "Leads are expected to have no partner, like the original registration"
        )
        # merge into one lead with multiple registrations
        final_lead = registrations.lead_ids._merge_opportunity(auto_unlink=False, max_length=None)
        self.assertEqual(final_lead.registration_ids, registrations)
        # update customer to trigger sync
        registrations[0].partner_id = self.event_customer
        self.assertEqual(registrations.lead_ids.partner_id, registrations[0].partner_id)

    @users('user_sales_manager')
    def test_merge_method_dependencies(self):
        """ Test if dependences for leads are not lost while merging leads. In
        this test leads are ordered as

        lead_w_contact -----------lead---seq=30
        lead_w_email -------------lead---seq=3
        lead_1 -------------------lead---seq=1
        lead_w_partner_company ---lead---seq=1----------------registrations
        lead_w_partner -----------lead---seq=False
        """
        TestLeadMergeCommon.merge_fields.append('registration_ids')

        registration = self.env['event.registration'].sudo().create({
            'partner_id': self.event_customer.id,
            'event_id': self.event_0.id,
            'lead_ids': [(4, self.lead_w_partner_company.id)],
        })
        self.assertEqual(self.lead_w_partner_company.registration_ids, registration)

        leads = self.env['crm.lead'].browse(self.leads.ids)._sort_by_confidence_level(reverse=True)
        with self.assertLeadMerged(self.lead_w_contact, leads,
                                   name=self.lead_w_contact.name,
                                   registration_ids=registration
                                   ):
            leads._merge_opportunity(auto_unlink=False, max_length=None)
