# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/8/24 13:40
"""
from odoo.http import request

#微服务唯一识别号转partner_id
def _ocean_platform_to_partner(ocean_platform_id):
	"""
	:param self:
	:param ocean_platform_id:
	:return:  int partner_id
	"""
	partner=request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(ocean_platform_id))])
	partner_id = partner.id
	return partner_id