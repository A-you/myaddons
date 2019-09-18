# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/8/1 14:54
"""

from odoo import api, http,fields
from odoo.http import request
import time
from datetime import timedelta

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token
import logging
_logger = logging.getLogger(__name__)

class MembershipMyController(http.Controller):

	# 积分查询
	def _points_dict(self, points_id):
		_dict = {
			'points_id': points_id.id,
			'name': points_id.name,
			'points': points_id.points,
			'service_type_id': points_id.service_type_id.id,
			'service_type_name': points_id.service_type_id.name
		}
		return _dict

	#钱包积分查询
	@validate_token
	@http.route('/membership/wallet/points/query', type='http', auth='none', csrf=False, methods=['GET'])
	def wallet_points_query(self, **kwargs):
		ocean_platform_id = kwargs.get('ocean_platform_id', False)
		if not ocean_platform_id:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', ocean_platform_id)])
		# partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', '8b76d745-a8e6-4a92-b89c-896b92bd47e5')])
		points_ids = request.env['membership.points.lines'].sudo().search([('partner_id', '=', partner_id.id)])
		data = [self._points_dict(points_id) for points_id in points_ids]
		print(data)
		return invalid_response([{"code": 200}, {"data": data}], "success", 200)

	#讯息查询
	def _message_dict(self,message_id):
		_dict = {
			'title': message_id.subject,
			'body': message_id.body
		}
		return _dict

	# 讯息查询
	@validate_token
	@http.route('/membership/my/message', type='http', auth='none', csrf=False, methods=['GET'])
	def message_query(self,**kwargs):
		ocean_platform_id = kwargs.get('ocean_platform_id', False)
		if not ocean_platform_id:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', ocean_platform_id)])
		domain = [('res_id', '=', partner_id.id),('subject','!=','')]
		message_ids = request.env['mail.message'].sudo().search(domain)
		data = [self._message_dict(message_id) for message_id in message_ids]
		return invalid_response([{"code": 200}, {"data": data}], "success", 200)


	#f服务查询
	def _service_line_dict(self, service_id):
		data = {
			"id": service_id.id,
			"name": service_id.membership_server.product_tmpl_id.name,
			"product_id": service_id.membership_server.id,
			"points": service_id.service_price,
			"state": service_id.state,
			"start_date": str(service_id.start_date),
			"end_date": str(service_id.end_date)
		}
		return data

	@validate_token
	@http.route('/membership/my/service', type='http', auth='none', csrf=False, methods=['GET'])
	def service_query_my(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)  # 暂定购买者自己
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		own_partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])
		service_line_ids = request.env['membership.service_line'].sudo().search(
			([('partner_id', '=', own_partner_id.id)]))
		if not service_line_ids:
			return invalid_response("fail", [{"code": 403}, {"data": "暂无数据"}], 200)
		data = [self._service_line_dict(service_id) for service_id in service_line_ids]
		return invalid_response("success", [{"code": 200}, {"data": data}], 200)

	# 会籍查询查询
	def _order_satet_dict(self, membership_line_id):
		print()
		_dict = {
			"create_date": str(membership_line_id.create_date),
			"name": membership_line_id.membership_id.name,
			"state": membership_line_id.state,
			"is_points": membership_line_id.is_points,
			"member_price": membership_line_id.member_price
		}
		return _dict

	#查询个人会籍
	@validate_token
	@http.route('/membership/invoice/query', type='http', auth='none', csrf=False, methods=['GET'])
	def query(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)  # 暂定购买者自己
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		partner_id= request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])
		if not partner_id:
			return invalid_response('Error', 'Parameter error')
		product_id = int(partner_id.id)
		membership_line_ids = request.env['membership.membership_line'].sudo().search([('partner', '=', product_id)])
		if not membership_line_ids:
			return invalid_response([{"code": 200}, {"data": "暂无数据"}], "success", 200)
		data = [self._order_satet_dict(membership_line_id) for membership_line_id in membership_line_ids]
		return invalid_response([{"code": 200}, {"data": data}], "success", 200)



	def handle_records_line(self,record):
		date = record.create_date.strftime("%Y-%m-%d")
		_dict= {
			"create_date": date,
			"name": record.name,
			'clause': record.clause,
			'points': record.points,
		}
		return _dict
	#支付记录
	# @validate_token
	# @http.route('/membership/payment/record',type='http', auth='none', csrf=False, methods=['GET'])
	# def query_payment_record(self,**kwargs):
	# 	own_platform_id = kwargs.get('own_platform_id', False)
	# 	past_times = kwargs.get('past_times', False)
	# 	type_id = kwargs.get('type_id', False)
	# 	if not own_platform_id:
	# 		return invalid_response('Error', 'Parameter error')
	# 	partner_id= request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])[0].id
	# 	if not partner_id:
	# 		return invalid_response('Error', 'Parameter error')
	# 	product_id = int(partner_id)
	# 	domain = [('partner_id', '=', product_id)]
	# 	if past_times:
	# 		try:
	# 			past_times = int(past_times)
	# 		except Exception as e:
	# 			return invalid_response('Error', 'past_times should be plastic surgery')
	# 		past_time = fields.datetime.now() + timedelta(days=-int(past_times))
	# 		domain.append(('create_date','>=',past_time))
	# 	if type_id:
	# 		try:
	# 			type_id = int(type_id)
	# 		except Exception as e:
	# 			return invalid_response('Error', 'type_id should be plastic surgery')
	# 		domain.append(('service_type_id', '>=', type_id))
	# 	records = request.env['membership.payment.record'].sudo().search(domain,order='create_date desc')
	# 	data = [self.handle_records_line(record) for record in records]
	# 	return invalid_response([{"code": 200}, {"data": data}], "success", 200)

	def _handle_service_line_dict(self,record):
		date = record.create_date.strftime("%Y-%m-%d")
		SERVICE_STATE = {
			'audit':'Waiting for Audit',
			'paid': 'Waiting for payment',
			'available': 'Available',
			'expired':"Expired",
			'unpaid':"Unpaid",
		}
		_dict = {
			"create_date": date,
			"name": record.membership_server.name,
			# 'clause': record.clause,
			'points': '-'+str(record.service_price),
			'order': record.service_order,
			'state': SERVICE_STATE[record.state]
		}
		return _dict

	def _handle_membership_line_dict(self,record):
		date = record.create_date.strftime("%Y-%m-%d")
		STATE = {
			    'none': 'Non Member',
			    'canceled': "Cancelled Member",
			    'old': 'Old Member',
		        'waiting':'Waiting Member',
		        'invoiced':'Invoiced Member',
		        'free':'Free Member',
		        'paid':'Paid Member',
		}
		_dict = {
			"create_date": date,
			"name": record.membership_id.name,
			# 'clause': record.clause,
			'points': '+' + str(record.membership_id.membership_points),
			"order": record.invoice_initial_code,
			'state': STATE[record.state]
		}
		return _dict

	#支付记录,更改后查询订单
	@http.route('/membership/payment/record', type='http', auth='none', csrf=False, methods=['GET'])
	def query_payment_record(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)
		past_times = kwargs.get('past_times', False)
		type_id = kwargs.get('type_id', False)
		page = kwargs.get('page',1)
		limit = kwargs.get('limit',10)
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		try:
			limit=int(limit)
			page=int(page)
		except Exception as e:
			return invalid_response('Error', 'Parameter error')
		if limit <1 or page<1:
			return invalid_response('Error', 'Parameter error')
		partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])[0]
		if not partner_id:
			return invalid_response('Error', 'Parameter error')
		_logger.info('>>/membership/invoice/query>>>%s'%partner_id.is_company)
		partner_id = int(partner_id.id)
		sdomain = [('partner_id', '=', partner_id)]
		mdomain = [('partner', '=', partner_id)]
		if past_times:
			try:
				past_times = int(past_times)
			except Exception as e:
				return invalid_response('Error', 'past_times should be plastic surgery')
			past_time = fields.datetime.now() + timedelta(days=-int(past_times))
			sdomain.append(('create_date', '>=', past_time))
			mdomain.append(('create_date', '>=', past_time))
		service_records = request.env['membership.service_line'].sudo().search(sdomain,order='create_date desc')
		member_records = request.env['membership.membership_line'].sudo().search(mdomain, order='create_date desc')
		service_data = [self._handle_service_line_dict(record) for record in service_records]
		member_data = [self._handle_membership_line_dict(record) for record in member_records]
		data = member_data+service_data
		data = sorted(data,key=lambda x:x['create_date'],reverse=True)
		offset = (page-1)*limit  #偏移等于页码乘每页大小
		upper = offset+limit
		data=data[offset:upper]
		return invalid_response([{"code": 200}, {"data": data}], "success", 200)

	#账单报表数据，目前给java提供数据查询
	@validate_token
	@http.route('/membership/bill/report',type='http', auth='none', csrf=False, methods=['GET'])
	def bill_report_query(self,**kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)
		date = kwargs.get('date',False)
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])[0].id
		if not partner_id:
			return invalid_response('Error', 'Parameter error')
		product_id = int(partner_id)
		domain = [('partner_id', '=', product_id)]
		if date:
			try:
				start_date = str(date)[:8] +"01"
				end_date = str(date)[:8] + "30"
				print()
			except Exception as e:
				return invalid_response('Error', 'type_id should be plastic surgery')
			else:
				domain.append(('create_date','>=',str(start_date)))
				domain.append(('create_date','<=',end_date))
		records = request.env['membership.payment.record'].sudo().search(domain, order='create_date desc')
		data = [self.handle_records_line(record) for record in records]
		count=len(data)
		return invalid_response([{"code": 200}, {"count": count,"data": data}], "success", 200)

	#处理以月为单位返回数据
	def _handle_month_payment(self,record):
		_dict={
			"date": record[0]+"-25",
			"title": "电子月结单内容",
			"count": record[1]
		}
		return _dict

	@validate_token
	@http.route('/membership/month/payment/query',type='http', auth='none', csrf=False, methods=['GET'])
	def month_payment_query(self,**kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])[0].id
		if not partner_id:
			return invalid_response('Error', 'Parameter error')
		sql="""SELECT to_char(create_date,'YYYY-MM') as d, count(id) as total_count 
		FROM membership_payment_record WHERE  partner_id=%d GROUP  BY d;"""%int(partner_id)
		request._cr.execute(sql)
		results = request._cr.fetchall()
		data = [self._handle_month_payment(record) for record in results]
		count= len(data)
		return invalid_response([{"code": 200}, {"count": count,"data": data}], "success", 200)

	#查询个人下面的所有公司
	@validate_token
	@http.route('/membership/personal/company/query',type='http', auth='none', csrf=False, methods=['GET'])
	def membership_personal_company_query(self):
		pass