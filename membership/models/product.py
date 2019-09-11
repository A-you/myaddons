# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

type = [
    ('currency', '通用'),
    ('service', '服务'),
    ('package', '企业包')
]

#购买会籍产品获得的等级
LEVEL = [
    (1, 'ZW'),
    (2, 'ZR'),
]

class Product(models.Model):
    _inherit = 'product.template'

    # 会员标志
    membership = fields.Boolean(help='Check if the product is eligible for membership.')
    # 会员开始时间
    membership_date_from = fields.Date(string='Membership Start Date',
                                       help='Date from which membership becomes active.')
    # 会员结束时间
    membership_date_to = fields.Date(string='Membership End Date',
                                     help='Date until which membership remains active.')
    product_type= fields.Selection(type,string='类型')

    # 有效期
    membership_validity_period = fields.Integer('Validity Period(month)', default=12)
    cost_price = fields.Float('Cost Price')
    # 可获得积分
    membership_points = fields.Integer(string='Membership Points')

    # 拥有服务
    membership_service_ids = fields.Many2many(comodel_name='hotel.services',
                                              string='Membership Service')

    # 购买该会籍获得对应的会员等级
    member_level = fields.Selection(LEVEL, string='Grading',default=1)
    member_title = fields.Selection([('starter','创客'),('affiliate','基本'),('associate','团队')],string='Available Title')
    #可获得称号权重，用于在会籍里显示
    weight_num = fields.Integer(string='Title Weight', default=0)

    #拥有的服务类别
    membership_service_type_ids = fields.One2many('product.hotel.service.line','product_tmpl_id', string='Membership Service')
    #迎新
    membership_new_arrivals_ids = fields.One2many('membership.new.arrivals','product_tmpl_id', string='迎新')
    # membership_service_ids = fields.One2many(comodel_name='membership.service', inverse_name='membership_product_id',
    #                                          string='Membership Service')
    # 约束 结束时间必须大于会员开始时间，否则报错
    _sql_constraints = [
        ('membership_date_greater', 'check(membership_date_to >= membership_date_from)',
         'Error ! Ending Date cannot be set before Beginning Date.')
    ]

    # 叼叼叼！！！在Python指定视图
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if self._context.get('product') == 'membership_product':
            if view_type == 'form':
                view_id = self.env.ref('membership.membership_products_form').id
            else:
                view_id = self.env.ref('membership.membership_products_tree').id
        return super(Product, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
