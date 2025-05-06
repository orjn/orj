# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class EventSaleReport(models.Model):
    _inherit = 'event.sale.report'

    is_published = fields.Boolean('Published Events', readonly=True)

    def _select_clause(self, *select):
        return super()._select_clause('event_event.is_published as is_published', *select)
