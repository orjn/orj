# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models
from orj.tools import SQL


class CrmPartnerReportAssign(models.Model):
    """ CRM Lead Report """
    _name = "crm.partner.report.assign"
    _auto = False
    _description = "CRM Partnership Analysis"

    partner_id = fields.Many2one('res.partner', 'Partner', required=False, readonly=True)
    grade_id = fields.Many2one('res.partner.grade', 'Grade', readonly=True)
    activation = fields.Many2one('res.partner.activation', 'Activation', index=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    date_review = fields.Date('Latest Partner Review')
    date_partnership = fields.Date('Partnership Date')
    country_id = fields.Many2one('res.country', 'Country', readonly=True)
    nbr_opportunities = fields.Integer('# of Opportunity', readonly=True)
    turnover = fields.Float('Turnover', readonly=True)
    date = fields.Date('Invoice Account Date', readonly=True)

    _depends = {
        'account.invoice.report': ['invoice_date', 'partner_id', 'price_subtotal', 'state', 'move_type'],
        'crm.lead': ['partner_assigned_id'],
        'res.partner': ['activation', 'country_id', 'date_partnership', 'date_review',
                        'grade_id', 'parent_id', 'user_id'],
    }

    @property
    def _table_query(self):
        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        return SQL(
            """
                SELECT
                    COALESCE(2 * i.id, 2 * p.id + 1) AS id,
                    p.id as partner_id,
                    (SELECT country_id FROM res_partner a WHERE a.parent_id=p.id AND country_id is not null limit 1) as country_id,
                    p.grade_id,
                    p.activation,
                    p.date_review,
                    p.date_partnership,
                    p.user_id,
                    (SELECT count(id) FROM crm_lead WHERE partner_assigned_id=p.id) AS nbr_opportunities,
                    i.price_subtotal as turnover,
                    i.invoice_date as date
                FROM
                    res_partner p
                    left join (%(account_invoice_report)s) i
                        on (i.partner_id=p.id and i.move_type in ('out_invoice','out_refund') and i.state='posted')
            """,
            account_invoice_report=self.env['account.invoice.report']._table_query,
        )
