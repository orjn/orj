# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging

from orj import api, models

_logger = logging.getLogger(__name__)


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    def _get_department_subtype(self):
        return self.search([
            ('res_model', '=', 'hr.department'),
            ('parent_id', '=', self.id)])

    def _update_department_subtype(self):
        for subtype in self:
            department_subtype = subtype._get_department_subtype()
            if department_subtype:
                department_subtype.write({
                    'name': subtype.name,
                    'default': subtype.default,
                })
            else:
                department_subtype = self.create({
                    'name': subtype.name,
                    'res_model': 'hr.department',
                    'default': False,
                    'parent_id': subtype.id,
                    'relation_field': 'department_id',
                })
            return department_subtype

    @api.model_create_multi
    def create(self, vals_list):
        result = super(MailMessageSubtype, self).create(vals_list)
        result.filtered(
            lambda st: st.res_model in ['hr.leave', 'hr.leave.allocation']
        )._update_department_subtype()
        return result

    def write(self, vals):
        result = super(MailMessageSubtype, self).write(vals)
        self.filtered(
            lambda subtype: subtype.res_model in ['hr.leave', 'hr.leave.allocation']
        )._update_department_subtype()
        return result
