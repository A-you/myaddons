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

class MembershipEventController(http.Controller):

	# @http.route("/membership/event/two/event",type='http', auth='none', csrf=False,methods=['GET'])
	# def query_event_two_menu(self,**kwargs):
	# 	type_id = kwargs.get('')
	# 	domain = [('x_parent', '=', None), ('type', '=', 'membership_service'), ('categ_id', '=', int(type_id))]
	# 	service_list = request.env['hotel.services'].sudo().search(domain, order="id")
	# 	pass
	def _handle_event_dict(sel,event_id):
		_dict = {
			"name": event_id.name
		}
		return dict

	@http.route("/membership/event/query",type='http', auth='none', csrf=False,methods=['GET'])
	def membership_event_query_route(self,**kwargs):
		keyword = kwargs.get('keyword',False)
		time_slot = kwargs.get('time_slot', False)
		time_day = kwargs.get('time_day', False)
		service_id = kwargs.get('service_id',False)

		domain = [('state', '=', 'confirm')]
		event_ids = request.env['event.event'].sudo().search(domain)
		data = [self._handle_event_dict(event_id) for event_id in event_ids]
		count = len(data)
		return invalid_response("success", [{"code": 200, "state": True},{"count":count}, {"data": data}], 200)
