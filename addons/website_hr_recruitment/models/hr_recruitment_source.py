# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from orj import api, fields, models


class RecruitmentSource(models.Model):
    _inherit = 'hr.recruitment.source'

    url = fields.Char(compute='_compute_url', string='Tracker URL')

    @api.depends('source_id', 'source_id.name', 'job_id', 'job_id.company_id')
    def _compute_url(self):
        for source in self:
            source.url = urls.url_join(source.job_id.get_base_url(), "%s?%s" % (
                source.job_id.website_url,
                urls.url_encode({
                    'utm_campaign': self.env.ref('hr_recruitment.utm_campaign_job').name,
                    'utm_medium': source.medium_id.name or self.env['utm.medium']._fetch_or_create_utm_medium('website').name,
                    'utm_source': source.source_id.name or None
                })
            ))
