# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/25 10:22
"""

from odoo import models,api,fields

class OceanMemberOpponent(models.Model):
	_name = 'ocean.member.opponent'
	_description = '表单中使用的竞争对手'

	name = fields.Char(string='竞争对手')
	# partner_ids = fields.Many2many('ocean.member.form1', string='OceanForms')
