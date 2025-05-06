# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, fields


class Challenge(models.Model):
    _inherit = 'gamification.challenge'

    challenge_category = fields.Selection(selection_add=[
        ('certification', 'Certifications')
    ], ondelete={'certification': 'set default'})
