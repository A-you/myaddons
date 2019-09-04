# encoding: utf-8

"""
@author: you
@site:
@time: 2019/8/12 14:28
"""

from odoo import models,fields,api

class MemberPaymentRecord(models.Model):
	_name = 'membership.payment.record'

	partner_id = fields.Many2one('res.partner',string='关联人')
	name = fields.Char(string='名称')
	clause = fields.Char(string='内容')
	points = fields.Char(string='积分')
	date = fields.Date(string='日期')
	service_type_id = fields.Many2one('hotel.service.type',string='服务类型')