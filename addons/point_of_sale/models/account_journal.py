# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from orj import fields, models, api, _
from orj.exceptions import ValidationError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pos_payment_method_ids = fields.One2many('pos.payment.method', 'journal_id', string='Point of Sale Payment Methods')

    @api.constrains('type')
    def _check_type(self):
        methods = self.env['pos.payment.method'].sudo().search([("journal_id", "in", self.ids)])
        if methods:
            raise ValidationError(_("This journal is associated with a payment method. You cannot modify its type"))

    def _check_no_active_payments(self):
        hanging_journal_entries = self.env['pos.payment'].search(
        [
            ('payment_method_id', 'in', self.pos_payment_method_ids.ids),
            ('session_id.state', '=', 'opened')
        ], limit=1)
        if(hanging_journal_entries):
            raise ValidationError(_("This journal is associated with payment method %(payment_method)s that is being used by order %(pos_order)s in the active pos session %(pos_session)s",
                payment_method=hanging_journal_entries.payment_method_id.name,
                pos_order=hanging_journal_entries.pos_order_id.name,
                pos_session=hanging_journal_entries.session_id.name))

    @api.ondelete(at_uninstall=False)
    def _unlink_journal_except_with_active_payments(self):
        for journal in self:
            journal._check_no_active_payments()

    def action_archive(self):
        self._check_no_active_payments()
        return super().action_archive()

    def _get_journal_inbound_outstanding_payment_accounts(self):
        res = super()._get_journal_inbound_outstanding_payment_accounts()
        account_ids = set(res.ids)
        for payment_method in self.sudo().pos_payment_method_ids:
            account_ids.add(payment_method.outstanding_account_id.id)
        return self.env['account.account'].browse(account_ids)

    @api.model
    def _ensure_company_account_journal(self):
        journal = self.search([
            ('code', '=', 'POSS'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not journal:
            journal = self.create({
                'name': _('Point of Sale'),
                'code': 'POSS',
                'type': 'general',
                'company_id': self.env.company.id,
            })
        return journal
