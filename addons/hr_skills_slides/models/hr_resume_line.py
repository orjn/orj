# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, api


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    display_type = fields.Selection(selection_add=[('course', 'Course')])
    channel_id = fields.Many2one('slide.channel', string="Course", readonly=True, index='btree_not_null')
    course_url = fields.Char(compute="_compute_course_url", default=False)

    @api.depends('channel_id')
    def _compute_course_url(self):
        for line in self:
            if line.display_type == 'course':
                line.course_url = line.channel_id.website_url
            else:
                line.course_url = False
