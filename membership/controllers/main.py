from odoo import api, http
from odoo.http import request

from odoo.addons.restful.common import *
from odoo.addons.restful.controllers.main import validate_token
import logging
_logger = logging.getLogger(__name__)



class MembershipController(http.Controller):

    #为公司添加用户或者为用户添加公司
    # @validate_token
    @http.route('/member/add/personal_or_company',type='http', auth='none', csrf=False, methods=['POST'])
    def add_personal_or_company(self,**kwargs):
        own_platform_id = kwargs.get('own_platform_id',False)
        other_platform_id = kwargs.get('other_platform_id',False)
        if not own_platform_id or not other_platform_id:
            return invalid_response('Error', 'Parameter error')
        #暂时可以说是个人
        own_partner_id = request.env['res.partner'].sudo().search([('ocean_platform_id','=',str(own_platform_id))])
        #必须是公司身份
        company_id = request.env['res.partner'].sudo().search([('ocean_platform_id', '=', str(other_platform_id))])
        #判断公司是不是公司
        if  not company_id.is_company:
            return invalid_response('Error', 'Parameter error rrr')
        try:
            # 插入到第三张表，个人与公司的关系表
            sql = """INSERT INTO personal_or_company_rel (current_id, relation_id)
    VALUES (%s,%s);"""%(own_partner_id.id,company_id.id)
            request._cr.execute(sql)
            request._cr.commit()
            #绑定公司与公司
            sql = """INSERT INTO company_to_personal_rel (company_id, personal_id)
                VALUES (%s,%s);""" % (company_id.id, own_partner_id.id)
            request._cr.execute(sql)
            request._cr.commit()
        except Exception as e:
            _logger.error('>>>>>/member/add/personal_or_company%s'%e)
            return invalid_response("fail",[{"code": 406}, {"data": "入参不对"}], 200)
        return invalid_response("success", [{"code": 200}, {"data": ""}], 200)

    #创建消息
    @validate_token
    @http.route('/member/mail/message/reply',type='http', auth='none', csrf=False, methods=['POST'])
    def mail_message_create_reply(self,**kwargs):
        res_id = kwargs.get('res_id', False) #接收者，对应查询时的发送者(作者)
        author_id = kwargs.get('author_id', False) #作者，对应查询时的接收者res_id
        subject = kwargs.get('subject',False)   #选填
        body = kwargs.get('body',False)
        if not res_id or not author_id or not body:
            return invalid_response("fail", [{"code": 403}, {"data": "Parameter error"}], 200)
        has_res_id = request.env['res.partner'].sudo().search([('id','=',res_id)])
        has_author_id = request.env['res.partner'].sudo().search([('id','=',author_id)])
        if not has_author_id or not has_res_id:
            return invalid_response("fail", [{"code": 403}, {"data": "Parameter error"}], 200)
        title = "来自:"+ has_author_id.name +"的回复"
        try:
            request.env['mail.message'].sudo().create({
                "subject": title,
                "body": body,
                "model": "res.partner",
                "res_id": 3,
                "message_type": "comment",
                "subtype_id":1,
                "email_from": has_author_id.email,
                "author_id":  has_author_id.id
            })
        except Exception as e:
            return invalid_response("fail", [{"code": 403}, {"data": "Failure to create"}], 200)
        return invalid_response("success", [{"code": 200}, {"data": "Successful response"}], 200)


