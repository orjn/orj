# -*- coding: utf-8 -*-
from orj import api, fields, models, _
from orj.exceptions import UserError, ValidationError
from orj.tools.misc import format_date, formatLang
from orj.tools.float_utils import float_repr
from orj.tools import groupby

from collections import defaultdict
from markupsafe import Markup, escape
from orj.tools import frozendict
import json

class AutomaticEntryWizard(models.TransientModel):
    _name = 'account.automatic.entry.wizard'
    _description = 'Create Automatic Entries'
    _check_company_auto = True

    # General
    action = fields.Selection([('change_period', 'Change Period'), ('change_account', 'Change Account')], required=True)
    move_data = fields.Text(compute="_compute_move_data") # JSON value of the moves to be created
    preview_move_data = fields.Text(compute="_compute_preview_move_data") # JSON value of the data to be displayed in the previewer
    move_line_ids = fields.Many2many('account.move.line')
    date = fields.Date(required=True, default=lambda self: fields.Date.context_today(self))
    company_id = fields.Many2one('res.company', required=True, readonly=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    percentage = fields.Float("Percentage", compute='_compute_percentage', readonly=False, store=True, help="Percentage of each line to execute the action on.")
    total_amount = fields.Monetary(compute='_compute_total_amount', store=True, readonly=False, currency_field='company_currency_id', help="Total amount impacted by the automatic entry.")
    journal_id = fields.Many2one('account.journal', required=True, readonly=False, string="Journal",
        check_company=True,
        domain="[('type', '=', 'general')]",
        compute="_compute_journal_id",
        inverse="_inverse_journal_id",
        help="Journal where to create the entry.")

    # change period
    account_type = fields.Selection([('income', 'Revenue'), ('expense', 'Expense')], compute='_compute_account_type', store=True)
    expense_accrual_account = fields.Many2one('account.account', readonly=False,
        check_company=True,
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'off_balance'))]",
        compute="_compute_expense_accrual_account",
        inverse="_inverse_expense_accrual_account",
    )
    revenue_accrual_account = fields.Many2one('account.account', readonly=False,
        check_company=True,
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'off_balance'))]",
        compute="_compute_revenue_accrual_account",
        inverse="_inverse_revenue_accrual_account",
    )
    lock_date_message = fields.Char(string="Lock Date Message", compute="_compute_lock_date_message")

    # change account
    destination_account_id = fields.Many2one(string="To", comodel_name='account.account', help="Account to transfer to.", check_company=True)
    display_currency_helper = fields.Boolean(string="Currency Conversion Helper", compute='_compute_display_currency_helper')
    # Technical field. Used to indicate whether or not to display the currency conversion tooltip. The tooltip informs a currency conversion will be performed with the transfer.

    @api.depends('company_id')
    def _compute_expense_accrual_account(self):
        for record in self:
            record.expense_accrual_account = record.company_id.expense_accrual_account_id

    def _inverse_expense_accrual_account(self):
        for record in self:
            record.company_id.sudo().expense_accrual_account_id = record.expense_accrual_account

    @api.depends('company_id')
    def _compute_revenue_accrual_account(self):
        for record in self:
            record.revenue_accrual_account = record.company_id.revenue_accrual_account_id

    def _inverse_revenue_accrual_account(self):
        for record in self:
            record.company_id.sudo().revenue_accrual_account_id = record.revenue_accrual_account

    @api.depends('company_id')
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = record.company_id.automatic_entry_default_journal_id

    def _inverse_journal_id(self):
        for record in self:
            record.company_id.sudo().automatic_entry_default_journal_id = record.journal_id

    @api.constrains('percentage', 'action')
    def _constraint_percentage(self):
        for record in self:
            if not (0.0 < record.percentage <= 100.0) and record.action == 'change_period':
                raise UserError(_("Percentage must be between 0 and 100"))

    @api.depends('percentage', 'move_line_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = (record.percentage or 100) * sum(record.move_line_ids.mapped('balance')) / 100

    @api.depends('total_amount', 'move_line_ids')
    def _compute_percentage(self):
        for record in self:
            total = (sum(record.move_line_ids.mapped('balance')) or record.total_amount)
            if total != 0:
                record.percentage = min((record.total_amount / total) * 100, 100)  # min() to avoid value being slightly over 100 due to rounding error
            else:
                record.percentage = 100

    @api.depends('move_line_ids')
    def _compute_account_type(self):
        for record in self:
            record.account_type = 'income' if sum(record.move_line_ids.mapped('balance')) < 0 else 'expense'

    @api.depends('action', 'move_line_ids')
    def _compute_lock_date_message(self):
        for record in self:
            record.lock_date_message = False
            if record.action == 'change_period':
                for aml in record.move_line_ids:
                    lock_date_message = aml.move_id._get_lock_date_message(aml.date, False)
                    if lock_date_message:
                        record.lock_date_message = lock_date_message
                        break

    @api.depends('destination_account_id')
    def _compute_display_currency_helper(self):
        for record in self:
            record.display_currency_helper = bool(record.destination_account_id.currency_id)

    @api.constrains('date', 'move_line_ids')
    def _check_date(self):
        for wizard in self:
            for move in wizard.move_line_ids.move_id:
                violated_lock_dates = move._get_violated_lock_dates(wizard.date, False)
                if violated_lock_dates:
                    raise ValidationError(_(
                        "The date selected is protected by: %(lock_date_info)s.",
                        lock_date_info=self.env['res.company']._format_lock_dates(violated_lock_dates)
                    ))

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if not set(fields) & set(['move_line_ids', 'company_id']):
            return res

        if self.env.context.get('active_model') != 'account.move.line' or not self.env.context.get('active_ids'):
            raise UserError(_('This can only be used on journal items'))
        move_line_ids = self.env['account.move.line'].browse(self.env.context['active_ids'])
        res['move_line_ids'] = [(6, 0, move_line_ids.ids)]

        if any(move.state != 'posted' for move in move_line_ids.mapped('move_id')):
            raise UserError(_('You can only change the period/account for posted journal items.'))
        if any(move_line.reconciled for move_line in move_line_ids):
            raise UserError(_('You can only change the period/account for items that are not yet reconciled.'))
        if any(line.company_id.root_id != move_line_ids[0].company_id.root_id for line in move_line_ids):
            raise UserError(_('You cannot use this wizard on journal entries belonging to different companies.'))
        res['company_id'] = move_line_ids[0].company_id.root_id.id

        allowed_actions = set(dict(self._fields['action'].selection))
        if self.env.context.get('default_action'):
            allowed_actions = {self.env.context['default_action']}
        if any(line.account_id.account_type != move_line_ids[0].account_id.account_type for line in move_line_ids):
            allowed_actions.discard('change_period')
        if not allowed_actions:
            raise UserError(_('No possible action found with the selected lines.'))
        res['action'] = allowed_actions.pop()
        return res

    def _get_cut_off_label_format(self):
        """ Get the translated format string used in cut-off labels """
        self.ensure_one()
        return _("Cut-off {label}") if self.percentage == 100 else _("Cut-off {label} {percent}%")

    def _get_move_dict_vals_change_account(self):
        line_vals = []

        # Group data from selected move lines
        counterpart_balances = defaultdict(lambda: defaultdict(lambda: 0))
        counterpart_distribution_amount = defaultdict(lambda: defaultdict(lambda: {}))
        grouped_source_lines = defaultdict(lambda: self.env['account.move.line'])

        for line in self.move_line_ids.filtered(lambda x: x.account_id != self.destination_account_id):
            counterpart_currency = line.currency_id
            counterpart_amount_currency = line.amount_currency

            if self.destination_account_id.currency_id and self.destination_account_id.currency_id != self.company_id.currency_id:
                counterpart_currency = self.destination_account_id.currency_id
                counterpart_amount_currency = self.company_id.currency_id._convert(line.balance, self.destination_account_id.currency_id, self.company_id, line.date)

            grouping_key = (line.partner_id, counterpart_currency)

            counterpart_balances[grouping_key]['amount_currency'] += counterpart_amount_currency
            counterpart_balances[grouping_key]['balance'] += line.balance
            if line.analytic_distribution:
                for account_id, distribution in line.analytic_distribution.items():
                    # For the counterpart, we will need to make a prorata of the different distribution of the lines
                    # This computes the total balance for each analytic account, for each counterpart line to generate
                    distribution_values = counterpart_distribution_amount[grouping_key]
                    distribution_values[account_id] = (line.balance * distribution + distribution_values.get(account_id, 0) * 100) / 100
            counterpart_balances[grouping_key]['analytic_distribution'] = counterpart_distribution_amount[grouping_key] or {}
            grouped_source_lines[(
                line.partner_id,
                line.currency_id,
                line.account_id,
                line.analytic_distribution and frozendict(line.analytic_distribution),
            )] += line

        # Generate counterpart lines' vals
        for (counterpart_partner, counterpart_currency), counterpart_vals in counterpart_balances.items():
            source_accounts = self.move_line_ids.mapped('account_id')
            counterpart_label = len(source_accounts) == 1 and _("Transfer from %s", source_accounts.display_name) or _("Transfer counterpart")

            # We divide the amount for each account by the total balance to reflect the lines counter-parted
            analytic_distribution = {
                account_id: (
                    100
                    if counterpart_currency.is_zero(counterpart_vals['balance'])
                    else 100 * distribution_amount / counterpart_vals['balance']
                )
                for account_id, distribution_amount in counterpart_vals['analytic_distribution'].items()
            }

            if not counterpart_currency.is_zero(counterpart_vals['amount_currency']) or not self.company_id.currency_id.is_zero(counterpart_vals['balance']):
                line_vals.append({
                    'name': counterpart_label,
                    'debit': counterpart_vals['balance'] > 0 and self.company_id.currency_id.round(counterpart_vals['balance']) or 0,
                    'credit': counterpart_vals['balance'] < 0 and self.company_id.currency_id.round(-counterpart_vals['balance']) or 0,
                    'account_id': self.destination_account_id.id,
                    'partner_id': counterpart_partner.id or None,
                    'amount_currency': counterpart_currency.round((counterpart_vals['balance'] < 0 and -1 or 1) * abs(counterpart_vals['amount_currency'])) or 0,
                    'currency_id': counterpart_currency.id,
                    'analytic_distribution': analytic_distribution,
                })

        # Generate change_account lines' vals
        for (partner, currency, account, analytic_distribution), lines in grouped_source_lines.items():
            account_balance = sum(line.balance for line in lines)
            if not self.company_id.currency_id.is_zero(account_balance):
                account_amount_currency = currency.round(sum(line.amount_currency for line in lines))
                line_vals.append({
                    'name': _('Transfer to %s', self.destination_account_id.display_name or _('[Not set]')),
                    'debit': account_balance < 0 and self.company_id.currency_id.round(-account_balance) or 0,
                    'credit': account_balance > 0 and self.company_id.currency_id.round(account_balance) or 0,
                    'account_id': account.id,
                    'partner_id': partner.id or None,
                    'currency_id': currency.id,
                    'amount_currency': (account_balance > 0 and -1 or 1) * abs(account_amount_currency),
                    'analytic_distribution': analytic_distribution,
                })

        # Get the lowest child company based on accounts used to avoid access error
        accounts = self.env['account.account'].browse([line['account_id'] for line in line_vals])
        companies = accounts.company_ids.filtered(lambda c: self.env.company in c.parent_ids) | self.env.company
        lowest_child_company = max(companies, key=lambda company: len(company.parent_ids))

        return [{
            'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
            'move_type': 'entry',
            'name': '/',
            'journal_id': self.journal_id.id,
            'company_id': lowest_child_company.id,
            'date': fields.Date.to_string(self.date),
            'ref': self.destination_account_id.display_name and _("Transfer entry to %s", self.destination_account_id.display_name or ''),
            'line_ids': [(0, 0, line) for line in line_vals],
        }]

    def _get_move_line_dict_vals_change_period(self, aml, date):
        # account.move.line data
        accrual_account = self.revenue_accrual_account if self.account_type == 'income' else self.expense_accrual_account
        reported_debit = aml.company_id.currency_id.round((self.percentage / 100) * aml.debit)
        reported_credit = aml.company_id.currency_id.round((self.percentage / 100) * aml.credit)
        reported_amount_currency = aml.currency_id.round((self.percentage / 100) * aml.amount_currency)
        name = self._format_strings(self._get_cut_off_label_format(), aml.move_id)

        if date == 'new_date':
            return [
                (0, 0, {
                    'name': name,
                    'debit': reported_debit,
                    'credit': reported_credit,
                    'amount_currency': reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': aml.account_id.id,
                    'partner_id': aml.partner_id.id,
                    'analytic_distribution': aml.analytic_distribution,
                }),
                (0, 0, {
                    'name': name,
                    'debit': reported_credit,
                    'credit': reported_debit,
                    'amount_currency': -reported_amount_currency,
                    'currency_id': aml.currency_id.id,
                    'account_id': accrual_account.id,
                    'partner_id': aml.partner_id.id,
                    'analytic_distribution': aml.analytic_distribution,
                }),
            ]
        return [
            (0, 0, {
                'name': name,
                'debit': reported_credit,
                'credit': reported_debit,
                'amount_currency': -reported_amount_currency,
                'currency_id': aml.currency_id.id,
                'account_id': aml.account_id.id,
                'partner_id': aml.partner_id.id,
                'analytic_distribution': aml.analytic_distribution,
            }),
            (0, 0, {
                'name': name,
                'debit': reported_debit,
                'credit': reported_credit,
                'amount_currency': reported_amount_currency,
                'currency_id': aml.currency_id.id,
                'account_id': accrual_account.id,
                'partner_id': aml.partner_id.id,
                'analytic_distribution': aml.analytic_distribution,
            }),
        ]

    def _get_lock_safe_date(self, date):
        # Use a reference move in the correct journal because _get_accounting_date depends on the journal sequence.
        reference_move = self.env['account.move'].new({'journal_id': self.journal_id.id, 'move_type': 'entry', 'invoice_date': date})
        return reference_move._get_accounting_date(date, False)

    def _get_move_dict_vals_change_period(self):

        def get_lock_safe_date(aml):
            return self._get_lock_safe_date(aml.date)

        # set the change_period account on the selected journal items

        ref_format = self._get_cut_off_label_format()
        move_data = {'new_date': {
            'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
            'move_type': 'entry',
            'line_ids': [],
            'ref': self._format_strings(ref_format, self.move_line_ids[0].move_id),
            'date': fields.Date.to_string(self.date),
            'journal_id': self.journal_id.id,
        }}
        # complete the account.move data
        for date, grouped_lines in groupby(self.move_line_ids, get_lock_safe_date):
            grouped_lines = list(grouped_lines)
            amount = sum(l.balance for l in grouped_lines)
            move_data[date] = {
                'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
                'move_type': 'entry',
                'line_ids': [],
                'ref': self._format_strings(ref_format, grouped_lines[0].move_id, amount),
                'date': fields.Date.to_string(date),
                'journal_id': self.journal_id.id,
            }

        # compute the account.move.lines and the total amount per move
        for aml in self.move_line_ids:
            for date in ('new_date', get_lock_safe_date(aml)):
                move_data[date]['line_ids'] += self._get_move_line_dict_vals_change_period(aml, date)

        move_vals = [m for m in move_data.values()]
        return move_vals

    @api.depends('move_line_ids', 'journal_id', 'revenue_accrual_account', 'expense_accrual_account', 'percentage', 'date', 'account_type', 'action', 'destination_account_id')
    def _compute_move_data(self):
        for record in self:
            if record.action == 'change_period':
                if any(line.account_id.account_type != record.move_line_ids[0].account_id.account_type for line in record.move_line_ids):
                    raise UserError(_('All accounts on the lines must be of the same type.'))
            if record.action == 'change_period':
                record.move_data = json.dumps(record._get_move_dict_vals_change_period())
            elif record.action == 'change_account':
                record.move_data = json.dumps(record._get_move_dict_vals_change_account())

    @api.depends('move_data')
    def _compute_preview_move_data(self):
        for record in self:
            preview_columns = [
                {'field': 'account_id', 'label': _('Account')},
                {'field': 'name', 'label': _('Label')},
                {'field': 'debit', 'label': _('Debit'), 'class': 'text-end text-nowrap'},
                {'field': 'credit', 'label': _('Credit'), 'class': 'text-end text-nowrap'},
            ]
            if record.action == 'change_account':
                preview_columns[2:2] = [{'field': 'partner_id', 'label': _('Partner')}]

            move_vals = json.loads(record.move_data)
            preview_vals = []
            for move in move_vals[:4]:
                preview_vals += [self.env['account.move']._move_dict_to_preview_vals(move, record.company_id.currency_id)]
            preview_discarded = max(0, len(move_vals) - len(preview_vals))

            record.preview_move_data = json.dumps({
                'groups_vals': preview_vals,
                'options': {
                    'discarded_number': _("%d moves", preview_discarded) if preview_discarded else False,
                    'columns': preview_columns,
                },
            })

    def do_action(self):
        move_vals = json.loads(self.move_data)
        self = self.with_context(skip_computed_taxes=True)
        if self.action == 'change_period':
            return self._do_action_change_period(move_vals)
        elif self.action == 'change_account':
            return self._do_action_change_account(move_vals)

    def _do_action_change_period(self, move_vals):
        accrual_account = self.revenue_accrual_account if self.account_type == 'income' else self.expense_accrual_account

        created_moves = self.env['account.move'].create(move_vals)
        created_moves._post()

        destination_move = created_moves[0]
        destination_move_offset = 0
        destination_messages = []
        accrual_move_messages = defaultdict(lambda: [])
        accrual_move_offsets = defaultdict(int)
        for move in self.move_line_ids.move_id:
            amount = sum((self.move_line_ids._origin & move.line_ids).mapped('balance'))
            accrual_move = created_moves[1:].filtered(lambda m: m.date == self._get_lock_safe_date(move.date))

            if accrual_account.reconcile and accrual_move.state == 'posted' and destination_move.state == 'posted':
                destination_move_lines = destination_move.mapped('line_ids').filtered(lambda line: line.account_id == accrual_account)[destination_move_offset:destination_move_offset+2]
                destination_move_offset += 2
                accrual_move_lines = accrual_move.mapped('line_ids').filtered(lambda line: line.account_id == accrual_account)[accrual_move_offsets[accrual_move]:accrual_move_offsets[accrual_move]+2]
                accrual_move_offsets[accrual_move] += 2
                (accrual_move_lines + destination_move_lines).filtered(lambda line: not line.currency_id.is_zero(line.balance)).reconcile()
            body = Markup("%(title)s<ul><li>%(link1)s %(second)s</li><li>%(link2)s %(third)s</li></ul>") % {
                'title': _("Adjusting Entries have been created for this invoice:"),
                'link1': self._format_move_link(accrual_move),
                'second': self._format_strings(_("cancelling {percent}%% of {amount}"), move, amount),
                'link2': self._format_move_link(destination_move),
                'third': self._format_strings(_("postponing it to {new_date}"), move, amount),
            }
            move.message_post(body=body)
            destination_messages += [
                self._format_strings(
                    escape(_("Adjusting Entry {link} {percent}%% of {amount} recognized from {date}")),
                    move, amount,
                )
            ]
            accrual_move_messages[accrual_move] += [
                self._format_strings(
                    escape(_("Adjusting Entry {link} {percent}%% of {amount} recognized on {new_date}")),
                    move, amount,
                )
            ]

        destination_move.message_post(body=Markup('<br/>\n').join(destination_messages))
        for accrual_move, messages in accrual_move_messages.items():
            accrual_move.message_post(body=Markup('<br/>\n').join(messages))

        # open the generated entries
        action = {
            'name': _('Generated Entries'),
            'domain': [('id', 'in', created_moves.ids)],
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('account.view_move_tree').id, 'list'), (False, 'form')],
        }
        if len(created_moves) == 1:
            action.update({'view_mode': 'form', 'res_id': created_moves.id})
        return action

    def _do_action_change_account(self, move_vals):
        new_move = self.env['account.move'].create(move_vals)
        new_move._post()

        # Group lines
        grouped_lines = defaultdict(lambda: self.env['account.move.line'])
        destination_lines = self.move_line_ids.filtered(lambda x: x.account_id == self.destination_account_id)
        for line in self.move_line_ids - destination_lines:
            grouped_lines[(line.partner_id, line.currency_id, line.account_id)] += line

        # Reconcile
        for (partner, currency, account), lines in grouped_lines.items():
            if account.reconcile:
                to_reconcile = lines + new_move.line_ids.filtered(lambda x: x.account_id == account and x.partner_id == partner and x.currency_id == currency)
                to_reconcile.reconcile()

            if destination_lines and self.destination_account_id.reconcile:
                to_reconcile = destination_lines + new_move.line_ids.filtered(lambda x: x.account_id == self.destination_account_id and x.partner_id == partner and x.currency_id == currency)
                to_reconcile.reconcile()

        # Log the operation on source moves
        acc_transfer_per_move = defaultdict(lambda: defaultdict(lambda: 0))  # dict(move, dict(account, balance))
        for line in self.move_line_ids:
            acc_transfer_per_move[line.move_id][line.account_id] += line.balance

        for move, balances_per_account in acc_transfer_per_move.items():
            message_to_log = self._format_transfer_source_log(balances_per_account, new_move)
            if message_to_log:
                move.message_post(body=message_to_log)

        # Log on target move as well
        new_move.message_post(body=self._format_new_transfer_move_log(acc_transfer_per_move))

        return {
            'name': _("Transfer"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': new_move.id,
        }

    # Transfer utils
    def _format_new_transfer_move_log(self, acc_transfer_per_move):
        transfer_format = Markup("<li>%s, <strong>%%(account_source_name)s</strong></li>") % \
            _("{amount} ({debit_credit}) from {link}")
        rslt = _(
            "This entry transfers the following amounts to %(destination)s",
            destination=Markup("<strong>%s</strong>") % self.destination_account_id.display_name,
        ) + Markup("<ul>%(transfer_logs)s</ul>") % {
            "transfer_logs": Markup().join(
                [
                    self._format_strings(transfer_format % {"account_source_name": account.display_name}, move, balance)
                    for move, balances_per_account in acc_transfer_per_move.items()
                    for account, balance in balances_per_account.items()
                    if account != self.destination_account_id  # Otherwise, logging it here is confusing for the user
                ],
            ),
        }
        return rslt

    def _format_transfer_source_log(self, balances_per_account, transfer_move):
        if not balances_per_account:
            return None

        transfer_format = Markup(
            _("{amount} ({debit_credit}) from <strong>{account_source_name}</strong> were transferred to <strong>{account_target_name}</strong> by {link}")
        )

        return Markup("<ul>%s</ul>") % Markup().join([
            Markup("<li>%s</li>") % \
                self._format_strings(transfer_format, transfer_move, balance, account.display_name)
            for account, balance in balances_per_account.items()
            if account != self.destination_account_id
        ])

    def _format_move_link(self, move):
        return move._get_html_link()

    def _format_strings(self, string, move, amount=None, account_source_name=''):
        return string.format(
            label=move.name or _('Adjusting Entry'),
            percent=float_repr(self.percentage, 2),
            name=move.name,
            id=move.id,
            amount=formatLang(self.env, abs(amount), currency_obj=self.company_id.currency_id) if amount else '',
            debit_credit=amount < 0 and _('C') or _('D') if amount else None,
            link=self._format_move_link(move),
            date=format_date(self.env, move.date),
            new_date=self.date and format_date(self.env, self.date) or _('[Not set]'),
            account_source_name=account_source_name,
            account_target_name=self.destination_account_id.display_name,
        )
