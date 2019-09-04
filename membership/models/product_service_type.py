from odoo import  fields, models

LEVEL = [
	('a','非会员'),
	('b','会员')
]

class ProductServiceType(models.Model):
	_name = 'product.service.type'
	_table = 'product_service_type_rel'

	hotel_service_type_id = fields.Many2one('hotel.service.type',string='服务类型')
	num = fields.Char(string='数量')



class InheritProductSupplierinfo(models.Model):
	_inherit = 'product.supplierinfo'
	_description = '继承扩展供应商'

	member_level = fields.Selection(LEVEL,'对应会员',copy=False, default='a')