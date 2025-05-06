# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _mailing_enabled = True
