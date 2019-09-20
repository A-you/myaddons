# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from datetime import date
from dateutil.relativedelta import relativedelta
from .membership import ServiceLine

POINTS_TYPE = [
    ('a', 'A'),
    ('b', 'B'),
    ('c', 'C'),
    ('d', 'D'),
]


class Invoice(models.Model):
    _inherit = 'account.invoice'

    use_points_wallet = fields.Selection([('personal', 'Personal'), ('company', 'Company')], readonly=True)
    use_points_type = fields.Selection(POINTS_TYPE, 'Use Points Type')
    is_points = fields.Boolean(readonly=True)  # 是否已经扣除积分

    personal_id = fields.Many2one('res.partner',string='购买人')

    invoice_initial_code = fields.Char(string='Invoice Code')

    @api.model
    def create(self, vals):
        # 生成服务订单编号
        if not self.invoice_initial_code:
            vals['invoice_initial_code'] = self.env['ir.sequence'].next_by_code(
                'membership.invoice_initial_code') or ''
        return super(Invoice, self).create(vals)

    @api.multi
    def action_cancel_draft(self):
        self.env['membership.membership_line'].search([
            ('account_invoice_line', 'in', self.mapped('invoice_line_ids').ids)
        ]).write({'date_cancel': False})
        return super(Invoice, self).action_cancel_draft()

    @api.multi
    def action_cancel(self):
        '''Create a 'date_cancel' on the membership_line object'''
        self.env['membership.membership_line'].search([
            ('account_invoice_line', 'in', self.mapped('invoice_line_ids').ids)
        ]).write({'date_cancel': fields.Date.today()})
        return super(Invoice, self).action_cancel()

    @api.multi
    def write(self, vals):
        '''Change the partner on related membership_line'''
        if 'partner_id' in vals:
            print("在这里创建的吗",self.mapped('invoice_line_ids').ids)
            self.env['membership.membership_line'].search([
                ('account_invoice_line', 'in', self.mapped('invoice_line_ids').ids)
            ]).write({'partner': vals['partner_id']})
        if 'state' in vals:
            print('发票状态改变')
            state = vals.get('state')
            print(state)
            #注释掉一下代码，去掉use_points_type和use_points_wallet的代码
            # 是否为支付成功，并且存在积分类型和钱包类别
            # print("self.invoice_line_ids[0]")
            # if state == 'paid' and self.invoice_line_ids[0].use_points_type \
            #         and self.invoice_line_ids[0].use_points_wallet:
            #     for line in self.invoice_line_ids:
            #         use_points_type = line.use_points_type
            #         use_points_wallet = line.use_points_wallet
            #         # 是否已经使用扣除过积分
            #         if not line.is_points:
            #             print('是否使用公司积分')
            #             print(line.use_points_wallet)
            #             if use_points_wallet == 'personal':
            #                 # 使用个人钱包
            #                 print('使用个人钱包')
            #                 if use_points_type == 'a':
            #                     membership_points_a = line.partner_id.membership_points_a  # 用户A积分余额
            #                     print('用户积分A：%d' % membership_points_a)
            #                     if membership_points_a and membership_points_a >= line.price_total:
            #                         new_membership_points_a = membership_points_a - line.price_total
            #                         line.partner_id.write({
            #                             'membership_points_a': new_membership_points_a,
            #                         })
            #                     else:
            #                         raise ValidationError("User A's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'b':
            #                     membership_points_b = line.partner_id.membership_points_b  # 用户B积分余额
            #                     print('用户B积分：%d' % membership_points_b)
            #                     if membership_points_b and membership_points_b >= line.price_total:
            #                         new_membership_points_b = membership_points_b - line.price_total
            #                         line.partner_id.write({
            #                             'membership_points_b': new_membership_points_b,
            #                         })
            #                     else:
            #                         raise ValidationError("User B's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'c':
            #                     membership_points_c = line.partner_id.membership_points_c  # 用户C积分余额
            #                     print('用户C积分：%d' % membership_points_c)
            #                     if membership_points_c and membership_points_c >= line.price_total:
            #                         new_membership_points_c = membership_points_c - line.price_total
            #                         line.partner_id.write({
            #                             'membership_points_c': new_membership_points_c,
            #                         })
            #                     else:
            #                         raise ValidationError("User C's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'd':
            #                     membership_points_d = line.partner_id.membership_points_d  # 用户D积分余额
            #                     print('用户D积分：%d' % membership_points_d)
            #                     if membership_points_d and membership_points_d >= line.price_total:
            #                         new_membership_points_d = membership_points_d - line.price_total
            #                         line.partner_id.write({
            #                             'membership_points_b': new_membership_points_d,
            #                         })
            #                     else:
            #                         raise ValidationError("User D's balance is not enough to pay for this purchase.")
            #             else:
            #                 # 使用公司钱包
            #                 print('使用公司钱包')
            #                 if not line.partner_id.parent_id:
            #                     raise ValidationError("User does not have a company.")
            #                 if use_points_type == 'a':
            #                     membership_points_a = line.partner_id.membership_company_points_a  # 公司A积分余额
            #                     print('用户公司A积分：%d' % membership_points_a)
            #                     if membership_points_a and membership_points_a >= line.price_total:
            #                         new_membership_points_a = membership_points_a - line.price_total
            #                         line.partner_id.partner_id.write({
            #                             'membership_points_a': new_membership_points_a,
            #                         })
            #                     else:
            #                         raise ValidationError(
            #                             "User company A's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'b':
            #                     membership_points_b = line.partner_id.membership_company_points_b  # 公司B积分余额
            #                     print('用户公司B积分：%d' % membership_points_b)
            #                     if membership_points_b and membership_points_b >= line.price_total:
            #                         new_membership_points_b = membership_points_b - line.price_total
            #                         line.partner_id.partner_id.write({
            #                             'membership_points_b': new_membership_points_b,
            #                         })
            #                     else:
            #                         raise ValidationError(
            #                             "User company B's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'c':
            #                     membership_points_c = line.partner_id.membership_company_points_c  # 公司C积分余额
            #                     print('用户公司C积分：%d' % membership_points_c)
            #                     if membership_points_c and membership_points_c >= line.price_total:
            #                         new_membership_points_c = membership_points_c - line.price_total
            #                         line.partner_id.partner_id.write({
            #                             'membership_points_c': new_membership_points_c,
            #                         })
            #                     else:
            #                         raise ValidationError(
            #                             "User company C's balance is not enough to pay for this purchase.")
            #                 elif use_points_type == 'd':
            #                     membership_points_d = line.partner_id.membership_company_points_d  # 公司D积分余额
            #                     print('用户公司D积分：%d' % membership_points_d)
            #                     if membership_points_d and membership_points_d >= line.price_total:
            #                         new_membership_points_d = membership_points_d - line.price_total
            #                         line.partner_id.partner_id.write({
            #                             'membership_points_b': new_membership_points_d,
            #                         })
            #                     else:
            #                         raise ValidationError(
            #                             "User company D's balance is not enough to pay for this purchase.")
            #
            #     for line in self.invoice_line_ids:
            #         # 设置已经成功扣除积分
            #         line.is_points = True

        return super(Invoice, self).write(vals)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    use_points_wallet = fields.Selection([('personal', 'Personal'), ('company', 'Company')], readonly=True)
    use_points_type = fields.Selection(POINTS_TYPE, 'Use Points Type')
    is_points = fields.Boolean(readonly=True)  # 是否已经扣除积分

    @api.multi
    def write(self, vals):
        MemberLine = self.env['membership.membership_line']
        res = super(AccountInvoiceLine, self).write(vals)
        today = fields.Date.today()
        for line in self.filtered(lambda line: line.invoice_id.type == 'out_invoice'):
            member_lines = MemberLine.search([('account_invoice_line', '=', line.id)])
            if line.product_id.membership and not member_lines:
                # Product line has changed to a membership product
                date_from = line.product_id.membership_date_from
                # date_to = line.product_id.membership_date_to
                date_to = today + relativedelta(years=1)
                if (date_from or date.min) < line.invoice_id.date_invoice < (date_to or date.min):
                    date_from = line.invoice_id.date_invoice

                print("111")
                MemberLine.create({
                    'partner': line.invoice_id.partner_id.id,
                    'membership_id': line.product_id.id,
                    'member_price': line.price_unit,
                    'date': fields.Date.today(),
                    'date_from': date_from,
                    'date_to': date_to,
                    'account_invoice_line': line.id,
                })
            if line.product_id and not line.product_id.membership and member_lines:
                # Product line has changed to a non membership product
                member_lines.unlink()
        return res

    @api.model
    def create(self, vals):
        MemberLine = self.env['membership.membership_line']
        MemberServiceLine = self.env['membership.service_line']
        today = fields.Date.today()

        invoice_line = super(AccountInvoiceLine, self).create(vals)
        # 创建会员记录
        if invoice_line.invoice_id.type == 'out_invoice' and invoice_line.product_id.membership and \
                not MemberLine.search([('account_invoice_line', '=', invoice_line.id)]):
            # Product line is a membership product
            date_from = invoice_line.product_id.membership_date_from
            date_to = today + relativedelta(years=1)

            # print(invoice_line.invoice_id.payment_ids[0].payment_date)
            # date_to = invoice_line.invoice_id.payment_ids[0].payment_date
            if (date_from and
                    date_from <
                    (invoice_line.invoice_id.date_invoice or date.min) <
                    (date_to or date.min)):
                date_from = invoice_line.invoice_id.date_invoice
            print("2ee2",invoice_line.invoice_id.personal_id.id)
            MemberLine.create({
                'partner': invoice_line.invoice_id.partner_id.id,
                'buyer_id': invoice_line.invoice_id.personal_id.id,
                'membership_id': invoice_line.product_id.id,
                'member_price': invoice_line.price_unit,
                'date': fields.Date.today(),
                'date_from': date_from,
                'date_to': date_to,
                'account_invoice_line': invoice_line.id,
            })
        # 创建会员服务记录
        if invoice_line.invoice_id.type == 'out_invoice' and \
                not MemberServiceLine.search([('account_invoice_line', '=', invoice_line.id)]) \
                and invoice_line.product_id.type == 'membership_service':
            service_line = MemberServiceLine.create({
                'partner_id': invoice_line.invoice_id.partner_id.id,
                'membership_server': invoice_line.product_id.id,
                'service_price': invoice_line.price_unit,
                'start_date': fields.Date.today(),
                'account_invoice_line': invoice_line.id,
                'is_use_company': invoice_line.invoice_id.use_points_wallet == 'company',
                # 'use_points_type': invoice_line.invoice_id.use_points_type,
            })
            print(service_line)
        return invoice_line
