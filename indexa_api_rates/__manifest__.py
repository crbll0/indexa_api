# -*- coding: utf-8 -*-
{
    'name': "Indexa API - Currency Rates",

    'summary': """
        consumes the api of Indexa.do to obtain the rate of USD and EUR in the Dominican Republic.
    """,

    'description': """
    """,

    'author': "GrowIT",
    'website': "",

    'category': 'Accounting',
    'version': '1',

    'depends': ['base', 'indexa_api_base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/ir.cron.xml',
    ],
    'installable': True,
    'auto_install': True,

}