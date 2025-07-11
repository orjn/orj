# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _can_be_edited_by_current_customer(self, *args, **kwargs):
        return super()._can_be_edited_by_current_customer(*args, **kwargs) and not self.is_mondialrelay
