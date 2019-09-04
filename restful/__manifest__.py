{
    'name': 'Odoo RESTFUL API',
    'version': '1.0.0',
    'category': 'API',
    'author': 'Wisdoo',
    'website': 'http://www.wisdoo.com.cn',
    'summary': 'Odoo RESTFUL API',
    'support': 'luhuan97@foxmail.com',
    'description': """
    RESTFUL API For Odoo
    """,
    'depends': [
        'web',
    ],
    'data': [
        'data/ir_config_param.xml',
        'views/ir_model.xml',
        'views/res_users.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/main_screenshot.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
