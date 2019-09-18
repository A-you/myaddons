# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/19 10:34
"""

from odoo import  fields,models,api

class MembershipPoints(models.Model):
	_name = 'membership.points.lines'
	_description = '积分详情列表'


	partner_id = fields.Many2one('res.partner',string='关联人')
	name=fields.Char(string='名称')
	points = fields.Float(string='积分')
	service_type_id = fields.Many2one('hotel.service.type',string='服务类型')   #只针对企业包的时候填写
	product_id = fields.Many2one('product.product',string='会籍产品')   #对应会籍
	member_type = fields.Char(string='Member Product Type')



class WelcomeNewArrivals(models.Model):
	_name = 'membership.new.arrivals'
	_description = '迎新模块'

	product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade', required=True,
	                                  index=True)
	hotel_service_type_id = fields.Many2one('hotel.service.type', string='服务类型', ondelete='restrict', required=True,
	                                        index=True)
	points = fields.Integer(string='点数')


#更改rec_name属性
class PricelistItem(models.Model):
	_inherit = 'product.pricelist.item'
	_rec_name = 'fixed_price'

	product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', ondelete='cascade',
        help="Specify a template if this rule only applies to one product template. Keep empty otherwise.")
	# @api.model
	# def name_create(self, name):
	# 	return self.create({'fixed_price': name}).name_get()[0]


class MemberTitle(models.Model):
	_name = 'membership.title'
	_description = "会员称号，例如团队称号"
	name = fields.Char(string='名称')
	partner_id = fields.Many2one('res.partner',string='关联人')
	product_id = fields.Many2one('product.product',string='关联会籍')
	title_type = fields.Char(string='会员种类')
	weight_num = fields.Integer(string='权重值',related='product_id.weight_num',store=True)


# print(PricelistItem.__mro__)
# print(PricelistItem.__bases__)

# print(PricelistItem.__dict__)
