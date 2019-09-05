# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/22 15:20
"""
from odoo import fields,api,models

class ServiceNeededLine(models.Model):
	_name = 'ocean.form.service.line'
	_description = '表单中服务需求属性'

	name = fields.Char(string='名称')
	partner_ids = fields.Many2many('ocean.member.form1',  string='OceanForms')
