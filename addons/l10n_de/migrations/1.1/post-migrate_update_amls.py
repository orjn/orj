# Part of Orj. See LICENSE file for full copyright and licensing details
from orj import api, SUPERUSER_ID


def migrate(cr, version):
    # The tax report line 68 has been removed as it does not appear in tax report anymore.
    # But, it was referenced in the account.sales.report
    # So, we update amls of this line only, to make this report consistent.

    env = api.Environment(cr, SUPERUSER_ID, {})
    country = env['res.country'].search([('code', '=', 'DE')], limit=1)
    tags_68 = env['account.account.tag']._get_tax_tags('68', country.id)
    tags_60 = env['account.account.tag']._get_tax_tags('60', country.id)

    if tags_68.filtered(lambda tag: tag.tax_negate):
        cr.execute(
            """
            UPDATE account_account_tag_account_move_line_rel
               SET account_account_tag_id = %s
             WHERE account_account_tag_id IN %s;
            """,
            [
                tags_60.filtered(lambda tag: tag.tax_negate)[0].id,
                tuple(tags_68.filtered(lambda tag: tag.tax_negate).ids)
            ]
        )

    if tags_68.filtered(lambda tag: not tag.tax_negate):
        cr.execute(
            """
            UPDATE account_account_tag_account_move_line_rel
               SET account_account_tag_id = %s
             WHERE account_account_tag_id IN %s;
            """,
            [
                tags_60.filtered(lambda tag: not tag.tax_negate)[0].id,
                tuple(tags_68.filtered(lambda tag: not tag.tax_negate).ids)
            ]
        )
