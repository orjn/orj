# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    candidate_properties_definition = fields.PropertiesDefinition('Candidate Properties')
    job_properties_definition = fields.PropertiesDefinition("Job Properties")
