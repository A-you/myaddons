# -*- coding: utf-8 -*-
{
    'name': "Change Header",

    'summary': """
	""",

    'description': """
        Change color of default odoo color
    """,

    'author': "wisdoo",
    'website': "https://www.wisdoo.com.cn",
    "license": "LGPL-3",
    "support": "",

    
    'category': 'Theme',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/header.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
