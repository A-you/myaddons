# encoding: utf-8

"""
@author: you
@site:
@time: 2019/9/17 17:34
"""

from odoo import  fields,models,api

class MemberDesire(models.Model):
	_name = 'membership.desire'
	_description = '愿望清单列表'


	partner_id = fields.Many2one('res.partner',string='关联人')
	name=fields.Char(string='名称')
	seller_id = fields.Many2one('product.supplierinfo',string='服务类型')   #只针对企业包的时候填写
	service_id = fields.Many2one('hotel.services',string='会籍产品')   #对应会籍
	member_type = fields.Char(string='Member Product Type')
	service_price = fields.Float(string='服务价格',related='seller_id.price', store=True)
