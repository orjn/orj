# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class MailTestSMS(models.Model):
    """ A model inheriting from mail.thread with some fields used for SMS
    gateway, like a partner, a specific mobile phone, ... """
    _description = 'Chatter Model for SMS Gateway'
    _name = 'mail.test.sms'
    _inherit = ['mail.thread']
    _mailing_enabled = True
    _order = 'name asc, id asc'

    name = fields.Char()
    subject = fields.Char()
    email_from = fields.Char()
    guest_ids = fields.Many2many('res.partner')
    phone_nbr = fields.Char()
    mobile_nbr = fields.Char()
    customer_id = fields.Many2one('res.partner', 'Customer')
    country_id = fields.Many2one('res.country')

    def _phone_get_number_fields(self):
        return ['phone_nbr', 'mobile_nbr']

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_id', 'guest_ids']


class MailTestSMSBL(models.Model):
    """ A model inheriting from mail.thread.phone allowing to test auto formatting
    of phone numbers, blacklist, ... """
    _description = 'SMS Mailing Blacklist Enabled'
    _name = 'mail.test.sms.bl'
    _inherit = ['mail.thread.phone']
    _mailing_enabled = True
    _order = 'name asc, id asc'

    name = fields.Char()
    subject = fields.Char()
    email_from = fields.Char()
    phone_nbr = fields.Char(compute='_compute_phone_nbr', readonly=False, store=True)
    mobile_nbr = fields.Char(compute='_compute_mobile_nbr', readonly=False, store=True)
    customer_id = fields.Many2one('res.partner', 'Customer')

    @api.depends('customer_id')
    def _compute_mobile_nbr(self):
        for phone_record in self.filtered(lambda rec: not rec.mobile_nbr and rec.customer_id):
            phone_record.mobile_nbr = phone_record.customer_id.mobile

    @api.depends('customer_id')
    def _compute_phone_nbr(self):
        for phone_record in self.filtered(lambda rec: not rec.phone_nbr and rec.customer_id):
            phone_record.phone_nbr = phone_record.customer_id.phone

    def _phone_get_number_fields(self):
        return ['phone_nbr', 'mobile_nbr']

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_id']


class MailTestSMSBLActivity(models.Model):
    """ A model inheriting from mail.thread.phone allowing to test auto formatting
    of phone numbers, blacklist, ... as well as activities management. """
    _description = 'SMS Mailing Blacklist Enabled with activities'
    _name = 'mail.test.sms.bl.activity'
    _inherit = [
        'mail.test.sms.bl',
        'mail.activity.mixin',
    ]
    _mailing_enabled = True
    _order = 'name asc, id asc'


class MailTestSMSOptout(models.Model):
    """ Model using blacklist mechanism and a hijacked opt-out mechanism for
    mass mailing features. """
    _description = 'SMS Mailing Blacklist / Optout Enabled'
    _name = 'mail.test.sms.bl.optout'
    _inherit = ['mail.thread.phone']
    _mailing_enabled = True
    _order = 'name asc, id asc'

    name = fields.Char()
    subject = fields.Char()
    email_from = fields.Char()
    phone_nbr = fields.Char()
    mobile_nbr = fields.Char()
    customer_id = fields.Many2one('res.partner', 'Customer')
    opt_out = fields.Boolean()

    def _phone_get_number_fields(self):
        return ['phone_nbr', 'mobile_nbr']

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_id']

    def _mailing_get_opt_out_list_sms(self, mailing):
        res_ids = mailing._get_recipients()
        return self.search([
            ('id', 'in', res_ids),
            ('opt_out', '=', True)
        ]).ids


class MailTestSMSPartner(models.Model):
    """ A model like sale order having only a customer, not specific phone
    or mobile fields. """
    _description = 'Chatter Model for SMS Gateway (Partner only)'
    _name = 'mail.test.sms.partner'
    _inherit = ['mail.thread']
    _mailing_enabled = True

    name = fields.Char()
    customer_id = fields.Many2one('res.partner', 'Customer')
    opt_out = fields.Boolean()

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_id']

    def _mailing_get_opt_out_list_sms(self, mailing):
        res_ids = mailing._get_recipients()
        return self.search([
            ('id', 'in', res_ids),
            ('opt_out', '=', True)
        ]).ids


class MailTestSMSPartner2Many(models.Model):
    """ A model like sale order having only a customer, not specific phone
    or mobile fields. """
    _description = 'Chatter Model for SMS Gateway (M2M Partners only)'
    _name = 'mail.test.sms.partner.2many'
    _inherit = ['mail.thread']
    _mailing_enabled = True

    name = fields.Char()
    customer_ids = fields.Many2many('res.partner', string='Customers')
    opt_out = fields.Boolean()

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_ids']

    def _mailing_get_opt_out_list_sms(self, mailing):
        res_ids = mailing._get_recipients()
        return self.search([
            ('id', 'in', res_ids),
            ('opt_out', '=', True)
        ]).ids

# ------------------------------------------------------------
# OTHER
# ------------------------------------------------------------

class SMSTestNotMailThread(models.Model):
    """ Models not inheriting from mail.thread but using some cross models
    capabilities of mail. """
    _name = 'sms.test.nothread'
    _description = "NoThread Model"

    name = fields.Char()
    company_id = fields.Many2one('res.company')
    customer_id = fields.Many2one('res.partner')

    def _mail_get_partner_fields(self, introspect_fields=False):
        return ['customer_id']
