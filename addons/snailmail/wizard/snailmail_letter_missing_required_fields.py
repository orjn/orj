
from orj import _, api, fields, models

class SnailmailLetterMissingRequiredFields(models.TransientModel):
    _name = 'snailmail.letter.missing.required.fields'
    _description = 'Update address of partner'

    partner_id = fields.Many2one('res.partner')
    letter_id = fields.Many2one('snailmail.letter')

    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')

    @api.model
    def default_get(self, fields):
        defaults = super(SnailmailLetterMissingRequiredFields, self).default_get(fields)
        if defaults.get('letter_id'):
            letter = self.env['snailmail.letter'].browse(defaults.get('letter_id'))
            defaults.update({
                'partner_id': letter.partner_id.id,
                'street': letter.street,
                'street2': letter.street2,
                'zip': letter.zip,
                'city': letter.city,
                'state_id': letter.state_id.id,
                'country_id': letter.country_id.id,
            })
        return defaults

    def update_address_cancel(self):
        self.letter_id.cancel()

    def update_address_save(self):
        address_data = {
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
        }
        self.partner_id.write(address_data)
        letters_to_resend = self.env['snailmail.letter'].search([
            ('partner_id', '=', self.partner_id.id),
            ('error_code', '=', 'MISSING_REQUIRED_FIELDS'),
        ])
        letters_to_resend.write(address_data)
        letters_to_resend.snailmail_print()
