# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import date
import calendar
from dateutil.relativedelta import relativedelta

from orj import models, api, _
from orj.osv import expression
from orj.tools import date_utils


class AccountMove(models.Model):
    _inherit = "account.account"

    @api.model
    def _get_date_period_boundaries(self, date_period, company):
        period_type = date_period["range_type"]
        year = date_period.get("year")
        month = date_period.get("month")
        quarter = date_period.get("quarter")
        day = date_period.get("day")
        if period_type == "year":
            fiscal_day = company.fiscalyear_last_day
            fiscal_month = int(company.fiscalyear_last_month)
            if not (fiscal_day == 31 and fiscal_month == 12):
                year += 1
            max_day = calendar.monthrange(year, fiscal_month)[1]
            current = date(year, fiscal_month, min(fiscal_day, max_day))
            start, end = date_utils.get_fiscal_year(current, fiscal_day, fiscal_month)
        elif period_type == "month":
            start = date(year, month, 1)
            end = start + relativedelta(months=1, days=-1)
        elif period_type == "quarter":
            first_month = quarter * 3 - 2
            start = date(year, first_month, 1)
            end = start + relativedelta(months=3, days=-1)
        elif period_type == "day":
            fiscal_day = company.fiscalyear_last_day
            fiscal_month = int(company.fiscalyear_last_month)
            end = date(year, month, day)
            start, _ = date_utils.get_fiscal_year(end, fiscal_day, fiscal_month)
        return start, end

    def _build_spreadsheet_formula_domain(self, formula_params, default_accounts=False):
        codes = [code for code in formula_params["codes"] if code]

        default_domain = expression.FALSE_DOMAIN
        if not codes:
            if not default_accounts:
                return default_domain
            default_domain = [('account_type', 'in', ['liability_payable', 'asset_receivable'])]

        company_id = formula_params["company_id"] or self.env.company.id
        company = self.env["res.company"].browse(company_id)
        start, end = self._get_date_period_boundaries(
            formula_params["date_range"], company
        )
        balance_domain = [
            ("account_id.include_initial_balance", "=", True),
            ("date", "<=", end),
        ]
        pnl_domain = [
            ("account_id.include_initial_balance", "=", False),
            ("date", ">=", start),
            ("date", "<=", end),
        ]
        # It is more optimized to (like) search for code directly in account.account than in account_move_line
        code_domain = expression.OR(
            [
                ("code", "=like", f"{code}%"),
            ]
            for code in codes
        )
        account_domain = expression.OR([code_domain, default_domain])
        account_ids = self.env["account.account"].with_company(company_id).search(account_domain).ids
        code_domain = [("account_id", "in", account_ids)]
        period_domain = expression.OR([balance_domain, pnl_domain])
        domain = expression.AND([code_domain, period_domain, [("company_id", "=", company_id)]])
        if formula_params["include_unposted"]:
            domain = expression.AND(
                [domain, [("move_id.state", "!=", "cancel")]]
            )
        else:
            domain = expression.AND(
                [domain, [("move_id.state", "=", "posted")]]
            )
        partner_ids = [int(partner_id) for partner_id in formula_params.get('partner_ids', []) if partner_id]
        if partner_ids:
            domain = expression.AND(
                [domain, [("partner_id", "in", partner_ids)]]
            )
        return domain

    @api.model
    def spreadsheet_move_line_action(self, args):
        domain = self._build_spreadsheet_formula_domain(args, default_accounts=True)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move.line",
            "view_mode": "list",
            "views": [[False, "list"]],
            "target": "current",
            "domain": domain,
            "name": _("Cell Audit"),
        }

    @api.model
    def spreadsheet_fetch_debit_credit(self, args_list):
        """Fetch data for ORJ.CREDIT, ORJ.DEBIT and ORJ.BALANCE formulas
        The input list looks like this:
        [{
            date_range: {
                range_type: "year"
                year: int
            },
            company_id: int
            codes: str[]
            include_unposted: bool
        }]
        """
        results = []
        for args in args_list:
            company_id = args["company_id"] or self.env.company.id
            domain = self._build_spreadsheet_formula_domain(args)
            MoveLines = self.env["account.move.line"].with_company(company_id)
            [(debit, credit)] = MoveLines._read_group(domain, aggregates=['debit:sum', 'credit:sum'])
            results.append({'debit': debit or 0, 'credit': credit or 0})

        return results

    @api.model
    def spreadsheet_fetch_residual_amount(self, args_list):
        """Fetch data for ORJ.RESUDUAL formulas
        The input list looks like this:
        [{
            date_range: {
                range_type: "year"
                year: int
            },
            company_id: int
            codes: str[]
            include_unposted: bool
        }]
        """
        results = []
        for args in args_list:
            company_id = args["company_id"] or self.env.company.id
            domain = self._build_spreadsheet_formula_domain(args, default_accounts=True)
            MoveLines = self.env["account.move.line"].with_company(company_id)
            [(amount_residual,)] = MoveLines._read_group(domain, aggregates=['amount_residual:sum'])
            results.append({'amount_residual': amount_residual or 0})

        return results

    @api.model
    def spreadsheet_fetch_partner_balance(self, args_list):
        """Fetch data for ORJ.PARTNER.BALANCE formulas
        The input list looks like this:
        [{
            date_range: {
                range_type: "year"
                year: int
            },
            company_id: int
            codes: str[]
            include_unposted: bool
            partner_ids: int[]
        }]
        """
        results = []
        for args in args_list:
            partner_ids = [partner_id for partner_id in args.get('partner_ids', []) if partner_id]
            if not partner_ids:
                results.append({'balance': 0})
                continue

            company_id = args["company_id"] or self.env.company.id
            domain = self._build_spreadsheet_formula_domain(args, default_accounts=True)
            MoveLines = self.env["account.move.line"].with_company(company_id)
            [(balance,)] = MoveLines._read_group(domain, aggregates=['balance:sum'])
            results.append({'balance': balance or 0})

        return results

    @api.model
    def get_account_group(self, account_types):
        data = self._read_group(
            [
                *self._check_company_domain(self.env.company),
                ("account_type", "in", account_types),
            ],
            ['account_type'],
            ['code:array_agg'],
        )
        mapped = dict(data)
        return [mapped.get(account_type, []) for account_type in account_types]
