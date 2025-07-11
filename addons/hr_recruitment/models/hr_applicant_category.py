# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from random import randint

from orj import fields, models


class ApplicantCategory(models.Model):
    _name = "hr.applicant.category"
    _description = "Category of applicant"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag Name", required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
