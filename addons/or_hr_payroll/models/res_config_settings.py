from orj import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_or_hr_payroll_account = fields.Boolean(string='Payroll Accounting')

