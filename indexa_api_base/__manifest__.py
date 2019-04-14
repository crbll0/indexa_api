# -*- coding: utf-8 -*-
{
    'name': "Indexa API - BASE",

    'summary': """
        Basis for using the Idexa API
    """,

    'description': """
    Create two entries in the ir.config_parameter model:
    -- key: indexa_api_url  value: https://api.indexa.do/api
    -- key: indexa_api_token  value: <put here you token>
    
    
    to get a token contact https://indexa.do/contactus and complete the form asking for a token.
    """,

    'author': "GrowIT",
    'website': "",

    'category': 'Uncategorized',
    'version': '1',

    'depends': ['base'],

    'data': [
        'data/ir.config.parameter.xml',
        'views/views.xml',
    ],
}