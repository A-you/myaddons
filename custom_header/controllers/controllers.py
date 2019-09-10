# -*- coding: utf-8 -*-
from odoo import http

# class CustomHeader(http.Controller):
#     @http.route('/custom_header/custom_header/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_header/custom_header/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_header.listing', {
#             'root': '/custom_header/custom_header',
#             'objects': http.request.env['custom_header.custom_header'].search([]),
#         })

#     @http.route('/custom_header/custom_header/objects/<model("custom_header.custom_header"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_header.object', {
#             'object': obj
#         })