# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    certification_validity_months = fields.Integer(
        'Validity', required=False,
        help='Specify the number of months the certification is valid after being awarded. '
             'Enter 0 for certifications that never expire.')
