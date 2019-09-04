# -*- coding: utf-8 -*-
from odoo import http

# class HotelService(http.Controller):
#     @http.route('/hotel_service/hotel_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotel_service/hotel_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotel_service.listing', {
#             'root': '/hotel_service/hotel_service',
#             'objects': http.request.env['hotel_service.hotel_service'].search([]),
#         })

#     @http.route('/hotel_service/hotel_service/objects/<model("hotel_service.hotel_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotel_service.object', {
#             'object': obj
#         })