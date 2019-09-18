#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/9/18 13:04
# @Author : Ymy
from odoo import api, http
from odoo.http import request
import json
import ast
import re

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token

from .base import BaseController
from .base import _ocean_platform_to_partner
import logging
_logger = logging.getLogger(__name__)

class MemberDesireController(http.Controller,BaseController):

	#添加愿望
	@http.route("/membership/desire/add",type='http',auth='none',csrf=False,methods=['POST'])
	def member_desire_add(self,**kwargs):
		personal_platform_id = kwargs.get('personal_platform_id', False)
		company_platform_id = kwargs.get('company_platform_id', False)
		service_id = kwargs.get('service_id', False)
		seller_id = kwargs.get('seller_id',False)
		if not personal_platform_id or not company_platform_id or not service_id:
			return self.res_err(600)
		if not seller_id:
			return self.res_err(600,data="请传入供应商id")
		if not service_id.isdigit():
			return self.res_err(603)
		company_id = _ocean_platform_to_partner(company_platform_id)
		personal_id = _ocean_platform_to_partner(personal_platform_id)
		if not company_id or not personal_id:
			return self.res_err(604)
		services = request.env['hotel.services'].sudo().search([("id","=",int(service_id))])
		if not services:
			return self.res_err(600,data="该服务不存在")
		#服务id
		desire_id = services[0].id
		product_tmpl_id = services[0].product_id.product_tmpl_id.id
		seller_ids = request.env['product.supplierinfo'].sudo().search(
			[('product_tmpl_id', '=', product_tmpl_id), ('id', '=', seller_id)])
		#供应商不存在或供应商与服务不吻合
		if not seller_ids:
			return self.res_err(605)
		try:
			desires=request.env['membership.desire'].sudo().create({
				"partner_id": personal_id, #关联到个人
				"company_id": company_id,
				"seller_id": seller_ids[0].id,
				"service_id": desire_id
			})
		except Exception as e:
			_logger.error("http>>/membership/desire/add,create membership.desire: %s"%e)
			return self.res_err(-1)
		else:
			# date = desires
			data = {
				"desire_order": desires.desire_order
			}
			return self.res_ok(data=data)

	#愿望查询处理
	def _handle_desire_list_dict(self,desire):
		# print(desire.seller_id.)
		_dict={
			"desire_id":desire.id,
			"name": desire.name,
			"desire_order": desire.desire_order,
			"seller_name": desire.seller_id.name.name,
			"price": desire.service_price,
			"seller_id":desire.seller_id.id
		}
		return _dict

	#愿望列表查询
	@http.route("/membership/desire/query/list", type='http', auth='none', csrf=False, methods=['GET'])
	def member_desire_query_list(self, **kwargs):
		personal_platform_id = kwargs.get('personal_platform_id', False)
		company_platform_id = kwargs.get('company_platform_id', False)
		page = kwargs.get('page',1) #分页用
		limit = kwargs.get('limit',20)
		if not personal_platform_id or not company_platform_id:
			return self.res_err(600)
		company_id = _ocean_platform_to_partner(company_platform_id)
		personal_id = _ocean_platform_to_partner(personal_platform_id)
		if not company_id or not personal_id:
			return self.res_err(604)
		domain = [("partner_id","=",personal_id),("company_id","=",company_id)]
		desires = request.env['membership.desire'].sudo().search(domain)
		data = [self._handle_desire_list_dict(desire) for desire in desires]
		return self.res_ok(count=len(data),data=data)


	@http.route("/membership/desire/delete", type='http', auth='none', csrf=False, methods=['POST'])
	def member_desire_delete(self,**kwargs):
		personal_platform_id = kwargs.get('personal_platform_id', False)
		company_platform_id = kwargs.get('company_platform_id', False)
		desire_ids = kwargs.get('desire_ids',False)

		print(desire_ids,type(desire_ids))
		print(ast.literal_eval(desire_ids),type(ast.literal_eval(desire_ids)))
		req = re.match(r'[\d\[\],]+$',desire_ids)
		# print(tt)
		if not req:
			return self.res_err(603)
		try:
			desire_list= ast.literal_eval(desire_ids)
		except Exception as e:
			_logger.error("http>>/membership/desire/delete,ast.literal_eval(desire_ids): %s"%e)
			return self.res_err(603)
		else:
			desires= request.env['membership.desire'].sudo().search([("id","in",desire_list)]).unlink()
			if desires:
				return self.res_ok()
			return self.res_err(-1)
