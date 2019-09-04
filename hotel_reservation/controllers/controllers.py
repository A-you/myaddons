from odoo import api, http
from odoo.http import request

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class ReservationController(http.Controller):

    @validate_token
    @http.route('/reservation/confirm/<id>', type='http', auth='none', csrf=False, methods=['POST'])
    def confirm_reservation(self, id=None, **payload):
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        reservation = request.env['hotel.reservation'].sudo().browse(_id, )
        if reservation:
            reservation = reservation[0]
            if reservation.state in ('confirm', 'done'):
                return invalid_response('Error', 'Reservation confirmed')
            reservation.confirmed_reservation()

        print(reservation)
        return valid_response({'id': _id, 'result': 'create invoice successful'})

    @validate_token
    @http.route('/reservation/pay/<id>', type='http', auth='none', csrf=False, methods=['POST'])
    def pay_reservation(self, id=None, **payload):
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        reservation = request.env['hotel.reservation'].sudo().browse(_id, )
        if reservation:
            reservation = reservation[0]
            invoice = reservation.new_folio_id.hotel_invoice_id
            invoice_id = reservation.new_folio_id.hotel_invoice_id.id
            print(invoice)
            if not invoice:
                return invalid_response('Invoice does not exist')  # 不存在发票

            if invoice.state not in ('open',):
                return invalid_response('Error', 'Only draft payments can be paid')
            sql = """SELECT payment_id FROM account_invoice_payment_rel WHERE invoice_id=%s LIMIT 1;""" % invoice_id
            request._cr.execute(sql)
            result = request._cr.fetchall()
            if not result:
                print('不存在')
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
                reservation.new_folio_id.action_done()
            else:
                print('存在')
                payment_id = result[0]
                payment = request.env['account.payment'].sudo().browse(payment_id, )
                payment.action_validate_invoice_payment()
                reservation.new_folio_id.action_done()

        print(reservation)
        return valid_response({'id': _id, 'result': 'payment successful'})
