from orj import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_sa_api_mode = fields.Selection(related='company_id.l10n_sa_api_mode', readonly=False)

    @api.depends('company_id')
    def _compute_company_informations(self):
        super()._compute_company_informations()
        for record in self:
            if self.company_id.country_code == 'SA':
                record.company_informations += _(
                    '\nBuilding Number: %(building_number)s, Plot Identification: %(plot_identification)s\nNeighborhood: %(neighborhood)s',
                    building_number=self.company_id.l10n_sa_edi_building_number,
                    plot_identification=self.company_id.l10n_sa_edi_plot_identification,
                    neighborhood=self.company_id.street2,
                )
