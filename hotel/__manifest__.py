# See LICENSE file for full copyright and licensing details.

{
    'name': 'Space Management',
    'version': '12.0.1.0.0',
    'author': 'Wisdoo',
    'category': 'Hotel',
    'website': 'http://www.wisdoo.com.cn',
    'depends': ['sale_stock', 'point_of_sale', 'hotel_service'],
    'summary': 'Space Management to Manage Folio and Site Configuration',
    'demo': ['data/hotel_data.xml'],
    'data': [
        'security/hotel_security.xml',
        'security/ir.model.access.csv',
        'data/hotel_sequence.xml',
        'report/report_view.xml',
        'report/hotel_folio_report_template.xml',
        'views/hotel_view.xml',
        'wizard/hotel_wizard.xml',
    ],
    'css': ['static/src/css/room_kanban.css'],
    'images': ['static/description/Hotel.png'],
    'application': True
}
