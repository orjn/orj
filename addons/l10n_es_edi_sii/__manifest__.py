# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

# Thanks to AEOrj and the Spanish community
# Specially among others Ignacio Ibeas, Pedro Baeza and Landoo

{
    'name': "Spain - SII EDI Suministro de Libros",
    'countries': ['es'],
    'version': '1.1',
    'category': 'Accounting/Localizations/EDI',
    'description': """
This module sends the taxes information (mostly VAT) of the
vendor bills and customer invoices to the SII.  It is called
Procedimiento G417 - IVA. Llevanza de libros registro.  It is
required for every company with a turnover of +6M€ and others can
already make use of it.  The invoices are automatically
sent after validation.

How the information is sent to the SII depends on the
configuration that is put in the taxes.  The taxes
that were in the chart template (l10n_es) are automatically
configured to have the right type.  It is possible however
that extra taxes need to be created for certain exempt/no sujeta reasons.

You need to configure your certificate and the tax agency.
    """,
    'depends': [
        'certificate',
        'l10n_es',
        'account_edi',
    ],
    'data': [
        'data/account_edi_data.xml',

        'views/account_move_views.xml',
        'views/l10n_es_edi_sii_certificate_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'demo/demo_certificate.xml',
        'demo/demo_company.xml',
    ],
    'external_dependencies': {
        'python': ['pyOpenSSL'],
    },
    'license': 'LGPL-3',
}
