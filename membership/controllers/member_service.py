# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/8/1 14:19
"""
MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

#会员等级对应供应商价格等级
#会员等级1表示zw,对应价格a也同时表示zw级，表示非会员价
MEMBER_LEVEL_PRICE = {
	1 : "a",
	2 : "b"
}
import json
from odoo import api, http
from odoo.http import request

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token

class MembershipServiceController(http.Controller):

	#微服务唯一识别号转partner_id
	def _ocean_platform_to_partner(self,ocean_platform_id):
		partner=request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(ocean_platform_id))])
		partner_id = partner.id
		return partner_id

	#查询是否有上级,暂时废弃
	def _handle_service_product_children(self, service_id):
		domain = [('x_parent', '=', service_id)]
		service_ids = request.env['hotel.services'].sudo().search(domain, order="id")
		if service_ids:
			return [self._service_product_dict(service_id) for service_id in service_ids]
		else:
			return []

	#构建返回服务字典
	def _service_product_dict(self, service_id):
		print("ss",service_id.name)
		_dict = {
			    'service_id': service_id.id,
                'name': service_id.product_id.product_tmpl_id.name,
                'categ_id': service_id.categ_id.id,
                # 'categ_name': service_id.categ_id.name,
                'price': service_id.product_id.product_tmpl_id.list_price,
                # 'children': self._handle_service_product_children(service_id.id),
			  'higher_id': service_id.x_parent.id if service_id.x_parent.id else False
		}
		return _dict

	#服务菜单查询
	@validate_token
	@http.route('/membership/service/menu/query',type='http', auth='none', csrf=False, methods=['GET'])
	def member_service_menu_query(self,**kwargs):
		type_id = kwargs.get('type_id',False)
		if not type_id:
			return invalid_response('Error', 'Parameter error')
		domain = [('x_parent','=',None),('type','=','membership_service'),('categ_id','=',int(type_id))]
		service_list = request.env['hotel.services'].sudo().search(domain, order="id")
		data = [self._service_product_dict(product_id) for product_id in service_list]
		count = len(data)
		return invalid_response("success", [{"code": 200}, {"count": count, "data": data}], 200)

	#服务查询，查询有哪些服务
	@validate_token
	@http.route('/membership/service/query', type='http', auth='none', csrf=False, methods=['GET'])
	def member_service_product(self,**kwargs):
		domain = [('x_parent','=',None),('type','=','membership_service')]
		service_id = kwargs.get('service_id',False)
		if service_id  and int(service_id):
			domain = [('x_parent','=', int(service_id))]
		service_list = request.env['hotel.services'].sudo().search(domain, order="id")
		data = [self._service_product_dict(product_id) for product_id in service_list]
		count = len(data)
		return invalid_response("success", [{"code": 200}, {"count":count,"data": data}], 200)

	#供应商查询及供应厂价格
	def _dict_seller_price(self,seller_id):
		"""
		seller_attr: p为三方供应商,o为二元桥供应商
		:param seller_id: 供应商id集合
		:return:
		"""
		_dict = {
			"seller_id": seller_id.id,
			"name": seller_id.name.name,
			"seller_attr": "p" if seller_id.name.name != "Self Confession" else "o",
			"price": seller_id.price,
			"member_level": 'member' if seller_id.member_level == 'b' else 'ordinary',
		}
		return _dict

	@http.route('/membership/service/seller/query', type='http', auth='none', csrf=False, methods=['GET'])
	def member_service_seller(self,service_id=None,ocean_platform_id=None):
		if not service_id:
			return invalid_response('Error', 'Parameter error')
		#会员价在java端处理。这里暂不做处理
		# try:
		# 	membership_level = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(ocean_platform_id))]).membership_level
		# except Exception as e:
		# 	return invalid_response('Error', 'Parameter error')
		product_tmpl_id = request.env['hotel.services'].sudo().search([('id','=',service_id)]).product_id.product_tmpl_id.id
		# price_level = MEMBER_LEVEL_PRICE[membership_level] or 'a'
		# domain = [('product_tmpl_id', '=', product_tmpl_id),('member_level','=',price_level)]
		domain = [('product_tmpl_id', '=', product_tmpl_id)]
		seller_ids = request.env['product.supplierinfo'].sudo().search(domain)
		data = [self._dict_seller_price(seller_id)  for seller_id in seller_ids]
		count= len(data)
		return invalid_response("success", [{"code": 200}, {"count":count,"data": data}], 200)


	#查询服务对应的积分情况，其实和查询本人所有积分有冲突，稳定后再更改
	def _handle_service_points_is_buy(self,points_id,price,service_categ_id):
		is_buy = False
		# print(price,service_categ_id)
		if points_id.member_type == 'service':
			service_list = []
			for y in points_id.product_id.membership_service_type_ids:
				service_list.append(y.hotel_service_type_id.id)
			if service_categ_id in service_list:
				# print("在服务类型里面的", '可以比较价格多少了')
				if points_id.points >= price:
					is_buy =True
		if points_id.member_type == 'package':
			if service_categ_id == points_id.service_type_id.id:
				# print("企业包有对应的类型", '可以比较价格多少了')
				if points_id.points>= price:
					is_buy = True
			else:
				pass
		if points_id.member_type == 'currency':
			# print("这是通用类型", "直接比较大小")
			if points_id.points >= price:
				is_buy = True
		return is_buy

	def _handle_service_points_dict(self,points_id,price,service_categ_id):
		_dict = {
			'points_id': points_id.id,
			'name': points_id.name,
			'points': points_id.points,
			'service_type_id': points_id.service_type_id.id,
			'service_type_name': points_id.service_type_id.name,
			'is_buy': self._handle_service_points_is_buy(points_id,price,service_categ_id),
		}
		return _dict

	@http.route('/membership/service/points/query', type='http', auth='none', csrf=False, methods=['GET'])
	def member_service_points(self,service_id=None,ocean_platform_id=None,**kwargs):
		seller_id = kwargs.get('seller_id',False)
		if not service_id or not ocean_platform_id:
			return invalid_response('Error', 'Parameter error')
		partner_id = self._ocean_platform_to_partner(ocean_platform_id)
		service=request.env['hotel.services'].sudo().search([('id','=',service_id)])
		product_tmpl_id = service[0].product_id.product_tmpl_id.id

		if not seller_id:
			return invalid_response('Error', 'Parameter error')

		#商品的价格，用于和积分做比较,没有考虑用服务商的价格做比较
		price = service.product_id.product_tmpl_id.list_price
		seller_ids = request.env['product.supplierinfo'].sudo().search(
			[('product_tmpl_id', '=', product_tmpl_id), ('id', '=', seller_id)])
		if not seller_ids:
			return invalid_response("fail", [{"code": 600, "state": False}, {"data": "亲，你输入的供应商id是错误的哦"}], 200)
		price = seller_ids[0].price
		service_categ_id = service.categ_id.id
		point_ids = request.env['membership.points.lines'].sudo().search([('partner_id','=',partner_id)])
		data = [self._handle_service_points_dict(point_id,price,service_categ_id) for point_id in point_ids]
		count = len(data)
		return invalid_response("success", [{"code": 200}, {"count":count,"data": data}], 200)

	def _product_service_ids(self, product_id):
		product = request.env['hotel_services'].sudo().search([('id', '=', product_id)])
		return product

	def _query_points_enough(self, partner_id, cate_id, product_price):
		class_points = request.env['membership.points.lines'].sudo().search(
			[('service_type_id', '=', cate_id), ('partner_id', '=', partner_id)]).points
		currency_points = request.env['membership.points.lines'].sudo().search(
			[('partner_id', '=', partner_id), ('name', '=', '通用')]).points
		if class_points > product_price or currency_points > product_price:
			return True
		return False



	@validate_token
	@http.route('/membership/service/invoice', type='http', auth='none', csrf=False, methods=['POST'])
	def service_invoice(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)  # 暂定自己
		other_platform_id = kwargs.get('other_platform_id', False)  # 暂时不用
		use_points_wallet = kwargs.get('use_points_wallet', False)  # 预留字段
		service_id = kwargs.get('service_id', False)
		#供应商
		seller_id = kwargs.get('seller_id', False)
		seller_price = kwargs.get('seller_price',False)
		if not own_platform_id:
			return invalid_response('Error', 'Parameter error')
		#还需再加入单条记录
		own_partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])
		# 选择公司付款，暂不用
		other_partner_id = request.env['res.partner'].sudo().search(
			[('ocean_platform_id', '=', str(other_platform_id))])
		product_ids = request.env['hotel.services'].sudo().search([('id', '=', int(service_id))])
		if not own_partner_id or not product_ids:
			return invalid_response('Error', 'There is no such use or the product')
		# 判断是否可以购买,传入产品类型和人的id
		cate_id = product_ids.categ_id.id
		#购买人的id
		partner_id = own_partner_id.id
		product_price = product_ids.product_tmpl_id.list_price
		if seller_id:
			product_price = seller_price
		is_buy = self._query_points_enough(partner_id, cate_id, product_price)
		if not is_buy:
			return invalid_response("fail", [{"code": 600, "state": False}, {"data": ""}], 200)
		if is_buy:
			state = "paid"
			#该服务是否需要审核
			if product_ids.auto_approval:
				state = "audit"
			#创建服务记录
			_line_dict = {
				"partner_id": int(partner_id),
				"membership_server": product_ids.id,
				"state": state,
				"seller_id": seller_id,
				"service_price": product_price
			}
			invoice_list=request.env['membership.service_line'].sudo().create(_line_dict)
			return invalid_response("success", [{"code": 200}, {"state": invoice_list[0].state, "invoice_id": invoice_list[0].id}], 200)

	#预约
	@validate_token
	@http.route('/membership/service/subscribe', type='http', auth='none', csrf=False, methods=['POST'])
	def service_subscribe(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)  # 暂定自己
		other_platform_id = kwargs.get('other_platform_id', False)  # 暂时不用
		use_points_wallet = kwargs.get('use_points_wallet', False)  # 预留字段
		service_id = kwargs.get('service_id', False)
		comments = kwargs.get('comments', False)
		# 供应商
		seller_id = kwargs.get('seller_id', False)
		seller_price = kwargs.get('seller_price', False)
		if not own_platform_id or not service_id:
			return invalid_response('Error', 'Parameter error')
		own_partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(own_platform_id))])
		product_ids = request.env['hotel.services'].sudo().search([('id', '=', int(service_id))])
		if not own_partner_id or not product_ids:
			return invalid_response('Error', 'Parameter error')
		product_price = product_ids.product_tmpl_id.list_price
		if seller_id:
			product_price=seller_price
		partner_id = own_partner_id.id
		_line_dict = {
			"partner_id": int(partner_id),
			"membership_server": product_ids.id,
			"state": "audit",
			"service_price": product_price,
			"seller_id": seller_id,
			'comments': comments
		}
		subscribe_list = request.env['membership.service_line'].sudo().create(_line_dict)
		return invalid_response("success",
		                        [{"code": 200},
		                         {"state": subscribe_list[0].state, "subscribe_id": subscribe_list[0].id}],
		                        200)

	# 改变服务的发票状态，进行扣积分，暂时先抽离出方法，以后可以单写接口,20190802不再使用
	def _product_service_pay(self, id):
		if not id:
			return invalid_response('Error', 'Parameter error')  # 参数错误

		invoice_id = int(id)

		invoice = request.env['account.invoice'].sudo().browse(invoice_id)
		print(invoice)
		if not invoice:
			return invalid_response('Error', 'Invoice does not exist')  # 不存在发票

		invoice.action_invoice_open()
		if invoice.state not in ('open',):
			return invalid_response('Error', 'Only draft payments can be paid')
		sql = """SELECT payment_id FROM account_invoice_payment_rel WHERE invoice_id=%s LIMIT 1;""" % invoice_id
		request._cr.execute(sql)
		result = request._cr.fetchall()
		if not result:
			print('不存在')
			journal = request.env['account.journal'].sudo().search(
				[('type', 'in', ('cash',)), ], limit=1)
			values = {
				'communication': invoice.reference or invoice.name or invoice.number,
				'payment_type': invoice.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound',
				'payment_method_id': 1,
				'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoice.type],
				'partner_id': invoice.partner_id[0].id,
				'amount': invoice.residual,
				'currency_id': invoice.currency_id.id,
				'journal_id': journal,
				'multi': False,
			}
			print(values)
			invoice.update({
				'payment_ids': [(0, 0, values)]
			})
			invoice.payment_ids[0].action_validate_invoice_payment()
		else:
			print('存在')
			payment_id = result[0]
			payment = request.env['account.payment'].sudo().browse(payment_id, )
			payment.action_validate_invoice_payment()
		return invalid_response("success", [{"code": 200, "state": True}, {"data": ""}], 200)

	def _product_service_pay_points(self,invoice_id,points_id):
		#查询出订单id
		service_id = request.env['membership.service_line'].sudo().search([('id','=',invoice_id)])
		points_line = request.env['membership.points.lines'].sudo().search([('id','=',points_id)])
		if service_id.state == "audit":
			return invalid_response("fail", [{"code": 605}, {"data": "The document awaits approval."}], 200)
		if service_id.service_price > points_line.points:
			return invalid_response("fail",[{"code": 600}, {"data": "Insufficient Integral"}],200)
		points_line.write({
			"points": points_line.points - service_id.service_price
		})
		service_id.write({
			"state": "available"
		})
		return invalid_response("success", [{"code": 200}, {"data": "Successful Purchase"}], 200)

	#服务支付api
	@validate_token
	@http.route('/membership/service/invoice/pay', type='http', auth='none', csrf=False, methods=['POST'])
	def service_invoice_pay(self, **kwargs):
		own_platform_id = kwargs.get('own_platform_id', False)  # 暂定购买者自己
		other_platform_id = kwargs.get('other_platform_id', False)  # 暂时不用
		#接收订单id和积分id
		invoice_id = kwargs.get('invoice_id', False)  # 预留字段
		points_id = kwargs.get('points_id',False)
		if not invoice_id or not points_id:
			return invalid_response('Error', 'Parameter error')
		result = self._product_service_pay_points(int(invoice_id),int(points_id))
		return result
