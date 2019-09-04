# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import calendar
import logging
import base64
from odoo.http import request
_logger = logging.getLogger(__name__)

class Membershiplinee(models.Model):
    _inherit = 'membership.membership_line'
    # 是否是服务
    is_service = fields.Boolean(default=False)



class MembershipService(models.Model):
    _inherit = 'membership.service_line'
    # 是否是服务
    is_service = fields.Boolean(default=True)


class MembershipConsumption(models.Model):
    _name = 'membership.consumption'

    partner_id = fields.Char('Partner ID')
    partner_binary = fields.Binary('Partner URL', attachment=True)
    time = fields.Date('Time')
    number = fields.Char('Number')
    url = fields.Char('url')

    @api.multi
    def auto_report_membership_statement(self):
        """
                                年份 date(2017-09-08格式)
                                :param date:
                                :return:本月第一天日期和本月最后一天日期
        """
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        year, month = str(date).split('-')[0], str(date).split('-')[1]
        end = calendar.monthrange(int(year), int(month))[1]
        start_date = '%s-%s-01' % (year, month)
        end_date = '%s-%s-%s' % (year, month, end)
        ids = self.env['res.partner'].sudo().search([('is_company', '=', False)])
        for i in range(len(ids)):
            record_id = self.env['membership.consumption'].sudo().search([('partner_id', '=', ids[i].id), ('time', '=', date)])
            if not record_id:
                # 生成pdf存入附件
                data = {'ids': ids, 'model': 'membership.membership_line',
                        'form': {'id': ids, 'start_date': start_date, 'end_date': end_date,
                                 'partner': [ids[i].id, ids[i].name]}}
                context = dict(request.env.context)
                report = request.env['ir.actions.report']._get_report_from_name(
                    'membership_statement.consumption_details_report')
                partner_binary=report.with_context(context).render_qweb_pdf(ids, data=data)[0]
                partner_binary1 = base64.encodestring(partner_binary)
                membership_consumption_ids = self.env['membership.consumption'].create({
                    'partner_id': ids[i].id,
                    'partner_binary': partner_binary1,
                    'time': date,
                })
                membership_consumption_id = membership_consumption_ids.id
                # 存url
                url = '/web/pdf_accessories?model=membership.consumption&id=%s&field=partner_binary' % (membership_consumption_id)
                self.env.cr.execute("update membership_consumption set url=%s where id = %s", (url, membership_consumption_id))


