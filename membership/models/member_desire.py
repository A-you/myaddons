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

	#暂定显示再个人身上，partner_id表示个人
	partner_id = fields.Many2one('res.partner',string='关联人')
	name=fields.Char(string='名称',related='service_id.name', store=True)
	seller_id = fields.Many2one('product.supplierinfo',string='供应商')   #只针对企业包的时候填写
	service_id = fields.Many2one('hotel.services',string='服务名称')   #对应服务
	member_type = fields.Char(string='Member Product Type')
	desire_price = fields.Float(string='服务价格',related='seller_id.price', store=True)
	company_id = fields.Many2one('res.partner',string='关联公司')
	desire_order = fields.Char(string='Desire Order')

	@api.model
	def create(self, vals):
		# 生成服务订单编号
		if not self.desire_order:
			vals['desire_order'] = self.env['ir.sequence'].next_by_code(
				'membership.desire') or ''
		return super(MemberDesire, self).create(vals)