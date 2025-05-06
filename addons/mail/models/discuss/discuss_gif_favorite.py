# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class GifFavorite(models.Model):
    _name = "discuss.gif.favorite"
    _description = "Save favorite GIF from Tenor API"

    tenor_gif_id = fields.Char("GIF id from Tenor", required=True)

    _sql_constraints = [
        (
            "user_gif_favorite",
            "unique(create_uid,tenor_gif_id)",
            "User should not have duplicated favorite GIF",
        ),
    ]
