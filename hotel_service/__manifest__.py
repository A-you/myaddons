# -*- coding: utf-8 -*-
{
    'name': "hotel_service",
    'summary': """
       Place summary here
       luhuan97@foxmail.com
    """,
    'description': """
        Long description of module's purpose
    """,
    'author': "Lecoo",
    'support': 'luhuan@wisdoo.com.cn',
    'website': "http://www.wisdoo.com.cn",
    'category': 'Uncategorized',
    'version': '0.1',
    # 依赖模块
    'depends': ['base', 'sale_stock', 'product','event','event_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/service_data.xml',
        'views/templates.xml',
        'views/views.xml',
        'views/inherit_even.xml',
    ],
    # 'application': True,
    'auto_install': False,
    # 'sequence': 1,
}
