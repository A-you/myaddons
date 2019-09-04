# -*- coding: utf-8 -*-
{
    'name': "membership_consumptiont",

    'description': """
        Membership expense bill
    """,

    'author': "dt",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'membership'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'report/report_template.xml',
        'report/report_view.xml',
        'wizards/membership_wizards.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': False,
}