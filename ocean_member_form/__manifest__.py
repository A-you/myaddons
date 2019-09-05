# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ocean Member Form',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Build your own dashboards',
    'description': """
    博志馆会员申请表
    """,
    'depends': ['base'],
    'data': [
        'views/form1.xml',
        'data/service_need_line_data.xml',
        'data/product_category_data.xml'
    ],
    'application': True,
}
