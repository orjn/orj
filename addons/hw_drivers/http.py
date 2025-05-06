# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj


def db_list(force=False, host=None):
    return []

orj.http.db_list = db_list
