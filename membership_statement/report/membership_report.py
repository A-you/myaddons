# See LICENSE file for full copyright and licensing details.

import datetime
from odoo import api, fields, models

class MembershipConsumptionDetailsReport(models.AbstractModel):
    _name = 'report.membership_statement.consumption_details_report'

    def get_membership_consumption_data(self, partner_id, start_date, end_date):
        sql = "select * from(select partner,membership_id,member_price,is_service,write_date from membership_membership_line  where write_date between %s and %s and partner = %s  union " \
              "select partner_id,membership_server,service_price,is_service,write_date from membership_service_line b where write_date between %s and %s and partner_id = %s" \
              ")aa order by write_date;"
        self.env.cr.execute(sql, (start_date, end_date, partner_id, start_date, end_date, partner_id))  # 执行SQL语句
        dicts = self.env.cr.dictfetchall()  # 获取SQL的查询结果
        if dicts:
            for l in range(len(dicts)):
                for k in dicts[l]:
                    if k == 'write_date':
                        write_date = datetime.datetime.strftime(dicts[l][k], '%Y-%m-%d')
                        dicts[l][k] = write_date
                    if k == 'is_service':
                        if dicts[l][k]:
                            membership_server = dicts[l]['membership_id']
                            membership_server_name = self.env['hotel.services'].search([('id', '=', membership_server)]).name
                            dicts[l]['membership_id'] = membership_server_name
                        else:
                            membership_id = dicts[l]['membership_id']
                            membership_name = self.env['product.template'].search([('id', '=', membership_id)]).name
                            dicts[l]['membership_id'] = membership_name
            return dicts



    @api.model
    def _get_report_values(self, docids, data):
        # """
        #                 年份 date(2017-09-08格式)
        #                 :param date:
        #                 :return:本月第一天日期和本月最后一天日期
        #         """
        # date = datetime.now().strftime('%Y-%m-%d')
        # year, month = str(date).split('-')[0], str(date).split('-')[1]
        # end = calendar.monthrange(int(year), int(month))[1]
        # start_date = '%s-%s-01' % (year, month)
        # end_date = '%s-%s-%s' % (year, month, end)
        if data is None:
            data = {}
        if not docids:
            docids = data['form'].get('docids')
        partner = data['form'].get('partner')
        partner_id = partner[0]
        partner_name = partner[1]
        start_date = datetime.datetime.strptime(data['form'].get('start_date'), '%Y-%m-%d')
        end_date = (datetime.datetime.strptime(data['form'].get('end_date'), '%Y-%m-%d')+datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        return {
            'data': data['form'],
            'partner_name': partner_name,
            'folio_data': self.get_membership_consumption_data(partner_id, start_date, end_date)
        }


