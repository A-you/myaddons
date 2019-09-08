# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/9/3 17:48
"""

from odoo import api, http
from odoo.http import request
import json
import ast

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token

from .base import BaseController

class MembershipEventController(http.Controller,BaseController):

	#构建二级菜单返回结果
	def _handle_event_parent_menu(self,service_id):
		res_id=request.env['hotel.services'].sudo().search([('x_parent', '=', service_id.id)], order="id")
		_dict={
			"service_id":service_id.id,
			"name":service_id.name,
			"has_child": 1 if res_id else 0
		}
		return _dict

	# @validate_token
	@http.route("/membership/event/parent/menu",type='http', auth='none', csrf=False,methods=['GET'])
	def query_event_two_menu(self,**kwargs):
		#專業交流
		type_id = kwargs.get('type_id',False)
		types = request.env['hotel.service.type'].sudo().search([('name','=','專業交流')])
		type_id = types[0].id
		domain = [('x_parent', '=', None), ('type', '=', 'membership_service'), ('categ_id', '=', int(type_id))]
		parent_services = request.env['hotel.services'].sudo().search(domain, order="id")
		parent_service_list = []
		for x in parent_services:
			parent_service_list.append(x.id)
		two_service_list = request.env['hotel.services'].sudo().search([('x_parent','in',parent_service_list)], order="id")
		# print("查询",two_service_list)
		data = [self._handle_event_parent_menu(service_id) for service_id in two_service_list]
		count = {
			"count": len(data)
		}
		return self.res_ok(count=count,data=data)

	@validate_token
	@http.route("/membership/event/child/menu", type='http', auth='none', csrf=False, methods=['GET'])
	def query_event_child_menu(self,**kwargs):
		service_id = kwargs.get('service_id',False)
		if not service_id:
			# return invalid_response('fail', [{"code": 401, "state": False}, {"data":"Parameter error"}], 200)  # 参数错误
			return self.res_err(603,data="Parameter error")
		two_service_list = request.env['hotel.services'].sudo().search([('x_parent', '=', int(service_id))],order="id")
		# print("查询",two_service_list)
		data = [self._handle_event_parent_menu(service_id) for service_id in two_service_list]
		count = len(data)
		return self.res_ok(count=count,data=data)
		# return invalid_response("success", [{"code": 200, "state": True},{"count":count}, {"data": data}], 200)

	def _handle_event_dict(sel,event_id):
		_dict = {
			"event_id": event_id.id,
			"name": event_id.name,
			"imag_url": event_id.image_url,
			"addr": "上海",
		}
		return _dict

	#全部查询
	@http.route("/membership/event/query/list/all",type='http', auth='none', csrf=False,methods=['GET'])
	def membership_event_query_route(self,**kwargs):
		keyword = kwargs.get('keyword',False)
		time_slot = kwargs.get('time_slot', False)
		time_day = kwargs.get('time_day', False)
		service_id = kwargs.get('service_id',False)

		domain = [('state', '=', 'confirm')]
		event_ids = request.env['event.event'].sudo().search(domain)
		print(event_ids)
		data = [self._handle_event_dict(event_id) for event_id in event_ids]
		count = len(data)
		return self.res_ok(count=count,data=data)
		# return invalid_response("success", [{"code": 200, "state": True},{"count":count}, {"data": data}], 200)

	#条件查询
	@http.route("/membership/event/query/list/condition",type='http', auth='none', csrf=False,methods=['GET'])
	def membership_event_query_condition(self,**kwargs):
		keyword = kwargs.get('keyword', False)
		time_slot = kwargs.get('time_slot', False)
		time_stamp = kwargs.get('time_stamp', False)   #前端选择日历后需转为时间戳
		service_id = kwargs.get('service_id', False)
		return self.membership_event_query_route()

	def _handle_event_detail_dict(self,event_id):
		_dict={
			"name": event_id.name,
			"event_id": event_id.id,
			"imag_url": event_id.image_url,
			"addr": event_id.event_addr,
			"hour_slot": str(event_id.start_hour).replace('.',':')+'-'+str(event_id.end_hour).replace('.',':'),
		}
		return _dict

	@http.route("/membership/event/query/detail",type='http', auth='none', csrf=False,methods=['GET'])
	def membership_event_query_detail(self,**kwargs):
		event_id = kwargs.get('event_id',False)
		if not event_id:
			# return invalid_response('fail', [{"code": 401, "state": False}, {"data":"Parameter error"}], 200)  # 参数错误
			return self.res_err(603,data="Parameter error")
		domain = [('id', '=', int(event_id))]
		event_ids = request.env['event.event'].sudo().search(domain)
		data = [self._handle_event_detail_dict(event_id) for event_id in event_ids]
		count = len(data)
		# return invalid_response("success", [{"code": 200, "state": True},{"count":count}, {"data": data}], 200)
		return self.res_ok(count=count,data=data)

	@http.route("/membership/event/subscribe",type='http',auth='none',csrf=False,methods=['POST'])
	def membership_event_subscribe(self,**kwargs):
		import datetime
		import time
		personal_platform_id = kwargs.get('personal_platform_id', False)
		event_id = kwargs.get('event_id', False)
		company_platform_id = kwargs.get('company_platform_id', False)

		domain = [('id', '=', int(event_id))]
		event = request.env['event.event'].sudo().search(domain)
		if not event:
			return self.res_err(603)
		#活动结束时间
		end_state = time.mktime(event.date_end.timetuple())
		#当前时间戳unix
		current_date = time.time()
		if current_date > end_state:
			print("已经结束了")
		#允许最大预约人数
		seats=event.seats_max
		#当前已注册的人数
		print(len(event.registration_ids))
		print("当前时间戳",(time.time()-time.mktime(event.create_date.timetuple()))/60)
		return self.res_ok(data='ok')


