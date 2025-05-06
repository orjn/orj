# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class Partner(models.Model):
    _inherit = 'res.partner'
    _mailing_enabled = True
