# encoding: utf-8

"""
@author: you
@site:
@time: 2019/7/23 18:11
"""

from odoo import api, http
from odoo.http import request
import json
import ast

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token



MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
PRODUCT_TYPE = {
	'currency': '通用',
	'service': '服务',
	'package': '企业包'
}

# REQUEST_PRICE_QUERY ={
# 	'hk_price': 'HK Pricelist',
# 	'hk__cost_price': 'HK CostPricelist',
# 	'cny_price': 'CNY Pricelist',
# 	'cny__cost_price': 'CNY CostPricelist'
# }

REQUEST_PRICE_QUERY ={
	'hk_price': 'HK Discount Pricelist',
	'hk__cost_price': 'HK SalesPricelist',
	'cny_price': 'CNY Discount Pricelist',
	'cny__cost_price': 'CNY SalesPricelist'
}
class MembershipProductController(http.Controller):

	#这类会籍产品空调够买到的积分类型和比率
	def _member_service_type(self, service_type):
		_dict = {
			'name': service_type.hotel_service_type_id.name,
			'percentage': service_type.percentage_ids.name
		}
		return _dict

	# 查询product.product中product_tmpl_id对应的id,后面创建发票时使用
	def _query_product_id(self, id):
		product_id = request.env['product.product'].sudo().search([('product_tmpl_id', '=', id)]).id
		return product_id

	#根据product_id返回product_tmpl_id
	def _query_product_tmpl_id(self,product_id):
		product_tmpl_id = request.env['product.product'].sudo().search([('id', '=', product_id)]).product_tmpl_id.id
		return product_tmpl_id

	#处理货币，港币和人民币
	def _handle_price_list(self, product_id):
		"""
		HK Discount Pricelist: 港币优惠价
		CNY Discount Pricelist: 人民币优惠价
		HK SalesPricelist: 港币原价
		CNY SalesPricelist:人民币原价
		:param product_id:
		:return:
		"""
		hk_price_id = request.env['product.pricelist'].sudo().search([('name', '=', 'HK Discount Pricelist')]).id
		hk__cost_price_id = request.env['product.pricelist'].sudo().search([('name', '=', 'HK SalesPricelist')]).id
		cny_price_id = request.env['product.pricelist'].sudo().search([('name', '=', 'CNY Discount Pricelist')]).id
		cny__cost_price_id = request.env['product.pricelist'].sudo().search([('name', '=', 'CNY SalesPricelist')]).id

		hk_price = request.env['product.pricelist.item'].sudo().search(
			[('product_tmpl_id', '=', product_id), ('pricelist_id', '=', hk_price_id)]).fixed_price
		hk__cost_price = request.env['product.pricelist.item'].sudo().search(
			[('product_tmpl_id', '=', product_id), ('pricelist_id', '=', hk__cost_price_id)]).fixed_price
		cny_price = request.env['product.pricelist.item'].sudo().search(
			[('product_tmpl_id', '=', product_id), ('pricelist_id', '=', cny_price_id)]).fixed_price
		cny__cost_price = request.env['product.pricelist.item'].sudo().search(
			[('product_tmpl_id', '=', product_id), ('pricelist_id', '=', cny__cost_price_id)]).fixed_price

		_dict = {
			'hk_price': hk_price,
			'hk__cost_price': hk__cost_price,
			'cny_price': cny_price,
			'cny__cost_price': cny__cost_price
		}

		return _dict

	#处理迎新
	def _handle_welcome_new(self,welcome_id):
		_dict = {
			"name": welcome_id.hotel_service_type_id.name,
			'points': welcome_id.points,
		}
		return _dict

	def _product_dict(self, each_goods):
		_dict = {
			'product_id': self._query_product_id(each_goods.id),
			# 'product_tmpl_id': each_goods.id,
			'name': each_goods.name,
			'product_type': each_goods.product_type,
			'membership_points': each_goods.membership_points,
			'welcome_new': [self._handle_welcome_new(welcome_id) for welcome_id in each_goods.membership_new_arrivals_ids],
			'price': self._handle_price_list(each_goods.id),
			# 'cost_price': each_goods.cost_price,
			# 'member_price': each_goods.list_price,
			'description': each_goods.description,
			'membership_validity_period': each_goods.membership_validity_period,
			'membership_service_type_ids': [self._member_service_type(service_type) for service_type in
			                                each_goods.membership_service_type_ids]
		}
		return _dict

	#查询会籍产品
	@validate_token
	@http.route('/membership/product', type='http', auth='none', csrf=False, methods=['GET'])
	def MembershipProduct(self):
		domain = [('membership', '=', True), ('type', '=', 'service')]
		goods_list = request.env['product.template'].sudo().search(domain, order="id")
		if not goods_list:
			return invalid_response("Error", "暂无数据", 404)
		data = [self._product_dict(each_goods) for each_goods in goods_list]
		return invalid_response([{"code": 200}, {"data": data}], "success", 200)


	#购物车数据查询，java端传来列表
	@validate_token
	@http.route('/membership/shopping/car/query',type='http', auth='none', csrf=False,methods=['GET'])
	def shopping_car_query(self,**kwargs):
		product_ids = []
		product_list = kwargs.get('product_list',False)
		if not product_list:
			return invalid_response("Error", "暂无数据", 404)
		product_ids += ast.literal_eval(product_list)
		data = []
		if len(product_ids) > 1:
			product_temp_list=request.env['product.product'].sudo().search([('id','in',product_ids)])
			data= [self._product_dict(each_goods.product_tmpl_id) for each_goods in product_temp_list ]
		count=len(data)
		return invalid_response("success", [{"code": 200, "state": True},{"count":count}, {"data": data}], 200)

	# 购买会籍
	@validate_token
	@http.route('/membership/invoice', type='http', auth='none', csrf=False, methods=['POST'])
	def invoice(self, **kwargs):
		from . import base
		#个人唯一标识符
		personal_platform_id = kwargs.get('personal_platform_id', False)
		product_id = kwargs.get('product_id', False)
		company_platform_id = kwargs.get('company_platform_id',False)
		price = kwargs.get('price',"")
		if not personal_platform_id and not product_id:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		#这里获得是一个对象
		if not price:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		try:
			# price = json.loads(price)
			price = ast.literal_eval(price)
		except Exception as e:
			return invalid_response('Error', 'Price Parameter error,Please enter the correct format')  # 参数错误
		if len(price.keys()) > 1:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		#价格name
		price_name = ''
		request_price = 0
		for key in price.keys():
			try:
				price_name = REQUEST_PRICE_QUERY[key]
				request_price = price[key]
			except Exception as e:
				return invalid_response('Error', 'Parameter error')  # 参数错误
		if len(price_name) == 0:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		product_tmpl_id = self._query_product_tmpl_id(product_id)
		pricelist_id = request.env['product.pricelist.item'].sudo().search(
			[('product_tmpl_id', '=', product_tmpl_id), ('pricelist_id', '=', price_name)])
		if not pricelist_id:
			return invalid_response("fail", [{"code": 603, "state": False}, {"data": "The product does not conform to the price"}], 200)
		amount_price = pricelist_id.fixed_price
		currency_id = pricelist_id.currency_id.id
		if int(amount_price) != int(request_price):
			return invalid_response("fail", [{"code": 600, "state": False}, {"data": "Prices do not coincide"}], 200)
		product_id = int(product_id)
		personal_id = base._ocean_platform_to_partner(personal_platform_id)
		company_id = base._ocean_platform_to_partner(company_platform_id)

		#会籍是购买在公司身份，所以传入公司
		partner = request.env['res.partner'].sudo().browse(company_id)
		if not partner:
			return invalid_response('Error', 'There is no such user.')

		# product = request.env['product.product'].sudo().browse(product_id)
		#这个价格是有问题的
		# price_dict = product.price_compute('list_price')
		# amount = price_dict.get(product_id) or False
		invoice_data = {
			'membership_product_id': product_id,
			'amount': amount_price,
			'personal_id': personal_id, #操作者
			'currency_id': currency_id,
		}
		# print(invoice_data)
		invoice_list = partner.create_membership_invoice(datas=invoice_data)
		# print(invoice_list)
		return valid_response([{'invoice_id': invoice_list[0], 'result': 'create invoice successful'}])

	# 会籍付款，成功返回，进行更改发票状态
	@validate_token
	@http.route('/membership/pay', type='http', auth='none', csrf=False, methods=['POST'])
	def pay(self, **payload):
		invoice_id = payload.get('invoice_id', False)
		if not invoice_id:
			return invalid_response('Error', 'Parameter error')  # 参数错误
		try:
			invoice_id = int(invoice_id)
		except Exception as e:
			return invalid_response('Error', 'Parameter error')

		invoice = request.env['account.invoice'].sudo().browse(invoice_id)
		if not invoice:
			return invalid_response('Error', 'Invoice does not exist')  # 不存在发票
		if invoice.state == 'paid':
			return invalid_response("fail", [{"code": 603, "state": False}, {"data": "Payment has been made and no further payment is required."}], 200)
		invoice.action_invoice_open()
		if invoice.state not in ('open',):
			return invalid_response('Error', 'Only draft payments can be paid')
		sql = """SELECT payment_id FROM account_invoice_payment_rel WHERE invoice_id=%s LIMIT 1;""" % invoice_id
		request._cr.execute(sql)
		result = request._cr.fetchall()
		if not result:
			journal = request.env['account.journal'].search(
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

		return valid_response([{'code': 1, 'result': 'pay successful'}])