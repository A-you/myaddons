# -*- coding: utf-8 -*-
from odoo import http

class MembershipStatement(http.Controller):
    @http.route('/membership_statement/membership_statement/', type='http', auth="public", csrf=False, methods=['GET'])
    def index(self, **kw):
        partner_id = kw.get('partner_id', "")
        start_date = kw.get('start_date', "")
        end_date = kw.get('end_date', "")



