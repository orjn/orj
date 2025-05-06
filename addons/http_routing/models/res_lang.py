# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models
from orj.addons.base.models.res_lang import LangDataDict


class ResLang(models.Model):
    _inherit = "res.lang"

    def _get_frontend(self) -> LangDataDict:
        """ Return the available languages for current request
        :return: LangDataDict({code: LangData})
        """
        return self._get_active_by('code')
