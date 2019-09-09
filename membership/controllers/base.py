# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/8/24 13:40
"""
from odoo.http import request

import json

import logging
_logger = logging.getLogger(__name__)


error_code = {
    -1: u'服务器内部错误',
    0: u'接口调用成功',
    403: u'禁止访问',
    405: u'错误的请求类型',
    501: u'数据库错误',
    502: u'并发异常，请重试',
    600: u'缺少参数',
    601: u'无权操作:缺少 token',
    602: u'签名错误',
	603: u'参数错误,Parameter error',
    604: u'无效的参数,不存在该用户',
    700: u'暂无数据',
    701: u'该功能暂未开通',
    702: u'资源余额不足',
    703: u'活动已结束',
    901: u'登录超时',
    300: u'缺少参数',
    400: u'域名错误',
    401: u'该域名已删除',
    402: u'该域名已禁用',
    404: u'暂无数据'
}

class BaseController(object):

    def _check_domain(self, sub_domain):
        wxapp_entry = request.env['wxapp.config'].sudo().search([('sub_domain', '=', sub_domain)])
        if not wxapp_entry:
            return self.res_err(404), None
        return None, wxapp_entry[0]

    def res_ok(self,count=0, data=None):
        ret = {'code': 0, 'msg': 'success'}
        if data:
            ret['data'] = data
            ret['count'] = count
        return request.make_response(
            headers={'Content-Type': 'json'},
            data=json.dumps(ret)
        )

    def res_err(self, code, data=None):
        ret = {'code': code, 'msg': error_code[code]}
        if data:
            ret['data'] = data
        return request.make_response(json.dumps(ret))


def convert_static_link(request, html):
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return html.replace('src="', 'src="{base_url}'.format(base_url=base_url))

#微服务唯一识别号转partner_id
def _ocean_platform_to_partner(ocean_platform_id):
    """
	:param self:
	:param ocean_platform_id:
	:return:  int partner_id
	"""
    partner_id = 0
    partner=request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(ocean_platform_id))])
    if partner:
        partner_id = partner.id
    return partner_id