# -*- coding: utf-8 -*-
{
    'name': "Indexa Api - Fuels",

    'summary': """
        consumes the api of Indexa.do to obtain the price of fuels in the Dominican Republic.
    """,

    'description': """
    """,

    'author': "GrowIT",
    'website': "",

    'category': 'Accounting',
    'version': '1',

    'depends': ['base', 'sale', 'indexa_api_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/ir.cron.xml',
    ],
}