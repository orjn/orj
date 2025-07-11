# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    social_twitter = fields.Char('X Account')
    social_facebook = fields.Char('Facebook Account')
    social_github = fields.Char('GitHub Account')
    social_linkedin = fields.Char('LinkedIn Account')
    social_youtube = fields.Char('Youtube Account')
    social_instagram = fields.Char('Instagram Account')
    social_tiktok = fields.Char('TikTok Account')
