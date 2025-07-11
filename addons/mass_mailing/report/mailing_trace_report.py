# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, tools


class MailingTraceReport(models.Model):
    _name = 'mailing.trace.report'
    _auto = False
    _description = 'Mass Mailing Statistics'

    # mailing
    name = fields.Char(string='Mass Mail', readonly=True)
    mailing_type = fields.Selection([('mail', 'Mail')], string='Type', default='mail', required=True)
    campaign = fields.Char(string='Mailing Campaign', readonly=True)
    scheduled_date = fields.Datetime(string='Scheduled Date', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('test', 'Tested'), ('done', 'Sent')],
        string='Status', readonly=True)
    email_from = fields.Char('From', readonly=True)
    # traces
    scheduled = fields.Integer(readonly=True)
    processing = fields.Integer(readonly=True)
    pending = fields.Integer(readonly=True)  # Used with SMS before a delivery report is received
    sent = fields.Integer(readonly=True)
    delivered = fields.Integer(readonly=True)
    error = fields.Integer(readonly=True)
    opened = fields.Integer(readonly=True)
    replied = fields.Integer(readonly=True)
    bounced = fields.Integer(readonly=True)
    canceled = fields.Integer(readonly=True)
    clicked = fields.Integer(readonly=True)

    def init(self):
        """Mass Mail Statistical Report: based on mailing.trace that models the various
        statistics collected for each mailing, and mailing.mailing model that models the
        various mailing performed. """
        tools.drop_view_if_exists(self.env.cr, 'mailing_trace_report')
        self.env.cr.execute(self._report_get_request())

    def _report_get_request(self):
        sql_select = 'SELECT %s' % ', '.join(self._report_get_request_select_items())
        sql_from = 'FROM %s' % ' '.join(self._report_get_request_from_items())
        sql_where_items = self._report_get_request_where_items()
        if sql_where_items and len(sql_where_items) == 1:
            sql_where = 'WHERE %s' % sql_where_items[0]
        elif sql_where_items:
            sql_where = 'WHERE %s' % ' AND '.join(sql_where_items)
        else:
            sql_where = ''
        sql_group_by = 'GROUP BY %s' % ', '.join(self._report_get_request_group_by_items())
        return f"CREATE OR REPLACE VIEW mailing_trace_report AS ({sql_select} {sql_from} {sql_where} {sql_group_by} )"

    def _report_get_request_select_items(self):
        return [
            'min(trace.id) as id',
            'utm_source.name as name',
            'mailing.mailing_type',
            'utm_campaign.name as campaign',
            'trace.create_date as scheduled_date',
            'mailing.state',
            'mailing.email_from',
            "COUNT(trace.id) as scheduled",
            "COUNT(trace.sent_datetime) as sent",
            "(COUNT(trace.id) - COUNT(trace.trace_status) FILTER (WHERE trace.trace_status IN ('outgoing', 'pending', 'process', 'error', 'bounce', 'cancel'))) as delivered",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'process') as processing",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'pending') as pending",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'error') as error",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'bounce') as bounced",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'cancel') as canceled",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'open') as opened",
            "COUNT(trace.trace_status) FILTER (WHERE trace.trace_status = 'reply') as replied",
            "COUNT(trace.links_click_datetime) as clicked",
        ]

    def _report_get_request_from_items(self):
        return [
            'mailing_trace as trace',
            'LEFT JOIN mailing_mailing as mailing ON (trace.mass_mailing_id=mailing.id)',
            'LEFT JOIN utm_campaign as utm_campaign ON (mailing.campaign_id = utm_campaign.id)',
            'LEFT JOIN utm_source as utm_source ON (mailing.source_id = utm_source.id)'
        ]

    def _report_get_request_where_items(self):
        return []

    def _report_get_request_group_by_items(self):
        return [
            'trace.create_date',
            'utm_source.name',
            'utm_campaign.name',
            'mailing.mailing_type',
            'mailing.state',
            'mailing.email_from'
        ]
