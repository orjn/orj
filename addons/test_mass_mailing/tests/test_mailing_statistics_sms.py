# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from lxml import html

from orj.addons.mail.tests.common import mail_new_test_user
from orj.addons.test_mass_mailing.tests.common import TestMassSMSCommon
from orj.tests.common import users
from orj.tests import tagged
from orj.tools import mute_logger

@tagged('digest', 'mass_mailing', 'mass_mailing_sms')
class TestMailingStatistics(TestMassSMSCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMailingStatistics, cls).setUpClass()

        cls.user_marketing_2 = mail_new_test_user(
            cls.env,
            groups='base.group_user,base.group_partner_manager,mass_mailing.group_mass_mailing_user',
            login='user_marketing_2',
            name='Marie Marketing',
            signature='--\nMarie'
        )
        mobile_numbers = [f'045300{x}{x}99' for x in range(6)] + ['0453000099'] * 4
        cls.records += cls._get_sms_test_records(mobile_numbers=mobile_numbers)
        cls.records = cls._reset_mail_context(cls.records)

    @users('user_marketing')
    @mute_logger('orj.addons.mass_mailing_sms.models.mailing_mailing', 'orj.addons.mail.models.mail_mail', 'orj.addons.mail.models.mail_thread')
    def test_mailing_statistics_sms(self):
        mailing = self.env['mailing.mailing'].browse(self.mailing_sms.ids)
        target_records = self.env['mail.test.sms'].browse(self.records.ids)
        mailing.write({'mailing_domain': [('id', 'in', target_records.ids)], 'user_id': self.user_marketing_2.id})
        mailing.action_put_in_queue()
        with self.mockSMSGateway():
            mailing.action_send_sms()

        # simulate some delivery reports
        for record_idx in range(4):
            self.gateway_sms_delivered(mailing, target_records[record_idx])

        # simulate some replies and clicks
        for record_idx in (0, 2, 3):
            self.gateway_sms_click(mailing, target_records[record_idx])

        for record_idx in (7, 8):
            record = target_records[record_idx]
            trace = mailing.mailing_trace_ids.filtered(lambda t: t.model == record._name and t.res_id == record.id)
            trace.set_bounced()

        self.assertEqual(mailing.clicked, 3)
        self.assertEqual(mailing.delivered, 4)
        self.assertEqual(mailing.opened, 3)
        self.assertEqual(mailing.sent, 16)
        self.assertEqual(mailing.scheduled, 0)
        self.assertEqual(mailing.canceled, 4)
        self.assertEqual(mailing.process, 0)
        self.assertEqual(mailing.pending, 10)
        self.assertEqual(mailing.bounced, 2)
        self.assertEqual(mailing.received_ratio, 25)
        self.assertEqual(mailing.opened_ratio, 21.43)
        self.assertEqual(mailing.bounced_ratio, 12.5)

        with self.mock_mail_gateway(mail_unlink_sent=True):
            mailing._action_send_statistics()

        self.assertEqual(len(self._new_mails), 1, "Mailing: a mail should have been created for statistics")
        mail = self._new_mails[0]
        # test email values
        self.assertEqual(mail.author_id, self.user_marketing_2.partner_id)
        self.assertEqual(mail.email_from, self.user_marketing_2.email_formatted)
        self.assertEqual(mail.email_to, self.user_marketing_2.email_formatted)
        self.assertEqual(mail.reply_to, self.company_admin.partner_id.email_formatted)
        self.assertEqual(mail.state, 'outgoing')
        # test body content: KPIs
        body_html = html.fromstring(mail.body_html)
        kpi_values = body_html.xpath('//table[@data-field="sms"]//*[hasclass("kpi_value")]/text()')
        self.assertEqual(
            [t.strip().strip('%') for t in kpi_values],
            ['25.0', str(float(mailing.clicks_ratio)), str(float(mailing.bounced_ratio))]
        )
        # test body content: clicks (a bit hackish but hey we are in stable)
        kpi_click_values = body_html.xpath('//table//tr[contains(@style,"color: #888888")]/td[contains(@style,"width: 30%")]/text()')
        first_link_value = int(kpi_click_values[0].strip().split()[1].strip('()'))
        self.assertEqual(first_link_value, mailing.clicked)

    @users('user_marketing')
    @mute_logger('orj.addons.mass_mailing_sms.models.mailing_mailing', 'orj.addons.mail.models.mail_mail', 'orj.addons.mail.models.mail_thread')
    def test_sent_delivered_sms(self):
        """ Test that if we get delivered trace status first instead of sent from
            providers for some reasons, the statistics for sent SMS will be correct. """
        mailing = self.env['mailing.mailing'].browse(self.mailing_sms.ids)
        target_records = self.env['mail.test.sms'].browse(self.records.ids)
        mailing.write({'mailing_domain': [('id', 'in', target_records.ids)], 'user_id': self.user_marketing_2.id})
        mailing.action_put_in_queue()
        with self.mockSMSGateway(force_delivered=True):
            mailing.action_send_sms()

        self.assertEqual(mailing.delivered, 16)
        self.assertEqual(mailing.sent, 16)
