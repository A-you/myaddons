# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/22 11:47
"""
from odoo import fields,models,api
class MemberOceanMagaNature(models.Model):
	_name = 'ocean.member.nature.business'
	_description = '在中国的经营模式'

	name = fields.Char(string='名称')

