# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from .models import model_multicompany

#
# Conditional installation of ore modules.
#
# This module is defined in community but some steps (defined with 'edition: "ore"')
# are only used to test ore. As it's not possible to direcly add ore
# modules dependencies, this post install hook will install accounting if exists.
#
def _auto_install_ore_dependencies(env):
    module_list = ['accountant']
    module_ids = env['ir.module.module'].search([('name', 'in', module_list), ('state', '=', 'uninstalled')])
    module_ids.sudo().button_install()
