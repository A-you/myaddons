
import logging
from odoo import http
from odoo.http import request
import json
import werkzeug
import datetime
import base64
_logger = logging.getLogger(__name__)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)

def json_response(rp):
    headers = {"Access-Control-Allow-Origin": "*",
               "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
               "Access-Control-Allow-Methods": "GET,POST,OPTIONS","Cache-Control":"no-cache"}
    return werkzeug.wrappers.Response(json.dumps(rp,cls=MyEncoder,ensure_ascii=False), mimetype='application/json;charset=utf-8',headers=headers)


class APIController(http.Controller):
    """."""
    @http.route(['/web/pdf'], csrf=False, type='http', auth="public", methods=['GET'])
    def content_pdf(self, start_date, end_date, partner_id):
        start_date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date1 = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        partner_id1 = int(partner_id)
        partner_name = request.env['res.partner'].sudo().search([('id', '=', partner_id1)]).name
        id = request.env['membership_statement.wizard'].sudo().search([('partner', '=', partner_id1), ('start_date', '=', start_date1), ('end_date', '=', end_date1)])
        if id:
            ids = id
        else:
            data_ids = request.env['membership_statement.wizard'].create({
                    'partner': partner_id,
                    'start_date': start_date,
                    'end_date': end_date
                })
            ids = data_ids.id
        report = request.env['ir.actions.report']._get_report_from_name('membership_statement.consumption_details_report')
        context = dict(request.env.context)
        data = {'ids': ids, 'model': 'membership.membership_line', 'form': {'id': ids, 'start_date': start_date, 'end_date': end_date, 'partner': [partner_id, partner_name]}}
        pdf = report.with_context(context).render_qweb_pdf(ids, data=data)[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/web/pdf_accessories'], csrf=False, type='http', auth="public", methods=['POST', 'OPTIONS', 'GET'])
    def content_image(self, model, id, field):
        content = request.env['ir.attachment'].sudo().search(
            [("res_model", '=', model), ("res_id", '=', id), ("res_field", '=', field)], limit=1).datas
        # _logger.info('++++++++++++++content:%s++++++++++++++++',str(content))
        headers = {"Access-Control-Allow-Origin": "*",
                   "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
                   "Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Cache-Control": "no-cache",
                   "Content-Type": "application/pdf"}
        if content:
            image_base64 = base64.b64decode(content)
        else:
            return json_response({'code': 404, 'id': '', 'msg': '没有找到。'})
        response = request.make_response(image_base64, headers)
        return response
