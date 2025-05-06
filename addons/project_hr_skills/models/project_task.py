# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    user_skill_ids = fields.One2many('hr.employee.skill', related='user_ids.employee_skill_ids')
