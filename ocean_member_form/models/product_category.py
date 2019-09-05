# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/23 11:17
"""
from odoo import fields,models,api

class OceanFormProductCategory(models.Model):
	_name = 'ocean.form.product.category'
	_description = "博志会员申请表中的产品分类"

	name = fields.Char(string='名称')
	partner_ids = fields.Many2many('ocean.member.form1', string='OceanForms')