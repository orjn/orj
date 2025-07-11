# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class EventTagCategory(models.Model):
    _name = 'event.tag.category'
    _inherit = ['event.tag.category', 'website.published.multi.mixin']

    def _default_is_published(self):
        return True
