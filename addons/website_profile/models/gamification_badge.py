# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class GamificationBadge(models.Model):
    _name = 'gamification.badge'
    _inherit = ['gamification.badge', 'website.published.mixin']
