# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _localization_use_documents(self):
        """ Uruguayan localization use documents """
        self.ensure_one()
        return self.account_fiscal_country_id.code == "UY" or super()._localization_use_documents()
