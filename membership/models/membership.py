# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
import urllib

_logger = logging.getLogger(__name__)

STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Cancelled Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]
# 非会员、取消会员资格、旧会员（已过期）、已创建发票的会员（未支付）、已支付会员




class MembershipLine(models.Model):
    _name = 'membership.membership_line'
    _rec_name = 'partner'
    _order = 'id desc'
    _description = 'Membership Line'

    # 关联的伙伴
    partner = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    # 对应的会籍商品
    membership_id = fields.Many2one('product.product', string="Membership", required=True)
    # 会籍开始日期
    date_from = fields.Date(string='From', readonly=True)
    # 会籍结束日期
    date_to = fields.Date(string='To', readonly=True)
    # 会籍取消日期
    date_cancel = fields.Date(string='Cancel date')
    # 加入日期
    date = fields.Date(string='Join Date',
                       help="Date on which member has joined the membership")
    # 会费
    member_price = fields.Float(string='Membership Fee',
                                digits=dp.get_precision('Product Price'), required=True,
                                help='Amount for the membership')
    #币种，用char型方便前端取值
    currency = fields.Char(string="币种")
    # 分析账户行
    account_invoice_line = fields.Many2one('account.invoice.line', string='Account Invoice line', readonly=True,
                                           ondelete='cascade')
    # 分析账户
    account_invoice_id = fields.Many2one('account.invoice', related='account_invoice_line.invoice_id', string='Invoice',
                                         readonly=True)
    # 公司
    company_id = fields.Many2one('res.company', related='account_invoice_line.invoice_id.company_id', string="Company",
                                 readonly=True, store=True)

    #操作员,购买者，一般为个人。若为只有职业者，则和partner相同
    buyer_id = fields.Many2one('res.partner', string='Buyer')

    # 状态
    # 非会员、取消会员资格、旧会员（已过期）、已创建发票的会员（未支付）、已支付会员
    state = fields.Selection(STATE, compute='_compute_state', string='Membership Status', store=True,
                             help="It indicates the membership status.\n"
                                  "-Non Member: A member who has not applied for any membership.\n"
                                  "-Cancelled Member: A member who has cancelled his membership.\n"
                                  "-Old Member: A member whose membership date has expired.\n"
                                  "-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n"
                                  "-Invoiced Member: A member whose invoice has been created.\n"
                                  "-Paid Member: A member who has paid the membership amount.")
    is_points = fields.Boolean(readonly=True)

    #处理购买通用类型会籍逻辑
    def _handle_currency_membership(self):
        pass

    # 处理购买服务类型会籍逻辑
    def _handle_service_membership(self):
        pass

    # 处理购买企业包类型会籍逻辑
    def _handle_package_membership(self):
        pass

    #获取最高等级的称号
    def _query_membership_title_max(self):
        id = self.partner.id
        # select_sql = """SELECT product_id FROM membership_product_tag_rel WHERE
        #                          partner_id=%s """ % (id)
        # self._cr.execute(select_sql)
        # res_ids = self._cr.fetchall()
        # print(res_ids)
        # res_list = []
        # for res_id in res_ids:
        #     res_list.append(res_id)
        # product_sql = """SELECT weight_num FROM product_template WHERE id in %s"""%res_list
        # self._cr.execute(product_sql)
        # product_ids = self._cr.fetchall()
        # print(product_ids)
        membership_dict = {
            "创客": "starter",
            "基本": "affiliate",
            "团队": "associate"
        }
        product_dict={}
        membership_name = ""
        membership_ids=self.env['membership.title'].sudo().search([("partner_id","=",id)])
        for x in membership_ids:
            product_dict[x.title_type] = x.weight_num or 0
        membership_name=max(product_dict,key=product_dict.get)
        return membership_name

    #向jav微服务中发送会籍信息
    def micro_services_membership(self):
        url = "http://111.231.55.146:8082/register/bindMembership"
        companyId=self.partner.ocean_platform_id
        membership_name = self._query_membership_title_max()
        _logger.info('>>>have welcome_new_points %s' % membership_name)
        postdata = urllib.parse.urlencode({
            "companyId": companyId,
            "membershipName": membership_name,
        }).encode('utf-8')
        req = urllib.request.Request(url=url, data=postdata, method='POST')
        res = urllib.request.urlopen(req)
        res_data = res.read().decode('utf-8')
        return True

    def _handle_package_new_points(self,hotel_service_type_id,welcome_new_points_dict):
        welcome_new_points = 0
        # 如果这个类型存在迎新包中，要进行迎新优惠处理
        if hotel_service_type_id in welcome_new_points_dict.keys():
            welcome_new_points = welcome_new_points_dict[hotel_service_type_id ]
        return welcome_new_points

    @api.depends('account_invoice_line.invoice_id.state',
                 'account_invoice_line.invoice_id.payment_ids',
                 'account_invoice_line.invoice_id.payment_ids.invoice_ids.type')
    def _compute_state(self):
        """
		Compute the state lines
		自动计算状态
		触发条件：
		1.发票状态
		2.发票付款
		3.发票类型：客户、供应商、客户退款、供应商退款
		"""

        Invoice = self.env['account.invoice']
        for line in self:

            #
            # 根据发票获取发票的状态和id
            # 根据发票行获取发票的id
            # 根据当前会员行id，查询会员行的发票行
            self._cr.execute('''
                SELECT i.state, i.id FROM
                account_invoice i
                WHERE
                i.id = (
                    SELECT l.invoice_id FROM
                    account_invoice_line l WHERE
                    l.id = (
                        SELECT  ml.account_invoice_line FROM
                        membership_membership_line ml WHERE
                        ml.id = %s
                        )
                    )
                ''', (line.id,))
            fetched = self._cr.fetchone()
            # 如果不存在发票则设置会员行的状态是未购买（取消状态）
            if not fetched:
                line.state = 'canceled'
                continue
            # 如果存在发票，取到发票的状态
            # 根据发票的状态给会员行设置不同的状态
            istate = fetched[0]
            if istate == 'draft':
                line.state = 'waiting'
            elif istate == 'open':
                line.state = 'invoiced'
            elif istate == 'paid':
                # 购买会员给积分
                # print('加钱啦！')
                if not line.is_points:
                    # today = fields.Date.today()
                    if not line.membership_id[0].membership_points:
                        points_rule = self.env['membership.points'].search([], limit=1)
                        if not points_rule:
                            raise ValidationError(_('找不到积分规则'))
                        points_rule = points_rule[0]
                        if not points_rule.currency_value:
                            raise ValidationError(_('兑换比例异常，规则货币金额为0'))
                        print(line.member_price / points_rule.currency_value)
                        # new_points = line.partner.membership_points + line.membership_id.membership_points
                        new_points = line.partner.membership_points + int(
                            line.member_price / points_rule.currency_value)
                    else:
                        new_points = line.membership_id[0].membership_points
                    # 如果当前购买的是通用包
                    if line.membership_id.product_type == 'currency':
                        # 判断当前用户是否存在通用类型的会员包
                        isExistence = self.env['membership.points.lines'].search(
                            [('name', '=', '通用'), ('partner_id', '=', line.partner.id)])
                        if isExistence:
                            print(isExistence.name)
                            isExistence.write({
                                "points": int(new_points) + isExistence.points
                            })
                        if not isExistence:
                            line.partner.membership_points_lines.create(
                                {"name": "通用",
                                 "points": new_points,
                                 "partner_id": line.partner.id,
                                 "member_type": "currency",
                                 "product_id": line.membership_id[0].id
                                 }
                            )
                    if line.membership_id.product_type == 'service':
                        #查看该会籍包有没有迎新活动
                        # wel_sql = """SELECT points FROM membership_new_arrivals
                        #  WHERE product_tmpl_id=%s """%line.membership_id.product_tmpl_id.id
                        # self._cr.execute(wel_sql)
                        # rr = self._cr.fetchone()
                        # print(rr)
                        # 判断有没有这个会籍的服务包，有的话，累加，没有则创建
                        hasService = self.env['membership.points.lines'].search(
                            [('product_id', '=', line.membership_id[0].id), ('partner_id', '=', line.partner.id)])
                        if hasService:
                            # print("有这种类型的",hasService)
                            hasService.write({
                                "points": int(new_points) + hasService.points
                            })
                        if not hasService:
                            # 迎新赠送点数
                            welcome_new_points = 0
                            if line.membership_id.membership_new_arrivals_ids:
                                welcome_new_points=line.membership_id.membership_new_arrivals_ids[0].points
                            #罢服务名字拼接起来
                            name_list = []
                            for x in line.membership_id[0].product_tmpl_id.membership_service_type_ids:
                                name_list.append(x.hotel_service_type_id.name)
                            name_str = ",".join(name_list)
                            _logger.info('>>>have welcome_new_points %s'%welcome_new_points)
                            line.partner.membership_points_lines.create(
                                {"name": "服务包:" + name_str,
                                 "points": new_points + welcome_new_points,
                                 "partner_id": line.partner.id,
                                 "member_type": "service",
                                 "product_id": line.membership_id[0].id,
                                 }
                            )
                    if line.membership_id.product_type == 'package':
                        #membership_product_tag_rel  插入会员称号，因考虑称号和是否有这会籍并不是直接相关，可能有会籍记录，但称号已过期
                        #所以不没有直接关联
                        membership_title=self.env['membership.title'].sudo().search([('title_type','=',line.membership_id.member_title),('partner_id','=',line.partner.id)])
                        if not membership_title:
                            self.env['membership.title'].sudo().create({
                                "name": line.membership_id[0].name,
                                "title_type": line.membership_id.member_title,
                                "partner_id": line.partner.id,
                                "product_id": line.membership_id[0].id
                            })
                        #迎新点数,这里用一个字典做存储
                        welcome_new_points_dict = {}

                        hasPackage = self.env['membership.membership_line'].search(
                            [('membership_id', '=', line.membership_id[0].id), ('partner', '=', line.partner.id)])                      #如果没有购买过这会籍，如果没有购买过，则进行查迎新
                        if  len(hasPackage) <=1:
                            if line.membership_id.membership_new_arrivals_ids:
                                for new_id in line.membership_id.membership_new_arrivals_ids:
                                    #以赠送服务类型的id作为键,赠送点数作为值
                                    welcome_new_points_dict[new_id.hotel_service_type_id.id]=new_id.points
                        _logger.info('>>>welcome_new_points_dict%s'%welcome_new_points_dict)
                        # 循环会员产品下面的服务类型
                        for x in line.membership_id.membership_service_type_ids:
                            member_point_id = self.env['membership.points.lines'].search(
                                [('service_type_id', '=', x.hotel_service_type_id.id),
                                 ('partner_id', '=', line.partner.id)])
                            #迎新点数
                            welcome_new_points = self._handle_package_new_points(x.hotel_service_type_id.id,
                                                                                 welcome_new_points_dict)
                            #如果这个类型存在，进行写的操作
                            if member_point_id:
                                print("ddddd",welcome_new_points)
                                member_point_id.write({
                                    "points": int(x.percentage_ids.name) / 100 * new_points + member_point_id.points +welcome_new_points
                                })
                            #如果不存在，进行创建的操作
                            if not member_point_id:
                                line.partner.membership_points_lines.create(
                                    {"name": x.hotel_service_type_id.name,
                                     "service_type_id": x.hotel_service_type_id.id,
                                     "points": int(x.percentage_ids.name) / 100 * new_points+welcome_new_points,
                                     "partner_id": line.partner.id,
                                     "member_type": "package",
                                     "product_id": line.membership_id[0].id
                                     }
                                )
                    #更新会员等级
                    if line.partner.membership_level<line.membership_id.member_level:
                        try:
                            line.partner.write({
                                'membership_level': line.membership_id.member_level
                            })
                        except Exception as e:
                            _logger.error('====>>Wrong Writing Membership Level %s' %e)
                    #创建交易记录，记录的作用为记录会籍和服务
                    self.env['membership.payment.record'].sudo().create({
                        "partner_id": line.partner.id,
                        "name": line.membership_id.name,
                        "clause": str(line.currency if line.currency else 'CNY') + str(line.member_price),
                        "points": '+'+str(new_points),
                        "date": fields.Date.today()
                    })

                    line.is_points = True
                self.micro_services_membership()
                line.state = 'paid'
                invoices = Invoice.browse(fetched[1]).payment_ids.mapped('invoice_ids')
                if invoices.filtered(lambda invoice: invoice.type == 'out_refund'):
                    # 如果发票的类型是客户退款，则会员行设置为取消状态
                    line.state = 'canceled'
            elif istate == 'cancel':
                line.state = 'canceled'
            else:
                line.state = 'none'

class Points(models.Model):
    _name = 'membership.points'
    _description = 'Membership Points'
    # 数值，货币，积分，生效时间，失效时间

    name = fields.Char('Name')
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    currency_value = fields.Integer(string='Value')
    points = fields.Integer(string='Points', default=1, readonly=True)
    effective_date = fields.Date(string='Effective Date')
    invalid_date = fields.Date(string='Invalid Date')

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for obj in self:
            obj.currency_id = main_company.currency_id.id


class ServiceCategory(models.Model):
    _name = 'membership.service.category'
    _description = 'Membership Service Category'
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The service category name already exists.')
    ]

    name = fields.Char('Name', required=True)


class Service(models.Model):
    _name = 'membership.service'
    _description = 'Membership Service'
    _order = 'category_id'
    _sql_constraints = [
        ('name_category_id_unique', 'UNIQUE(name,category_id)', 'Service names and categories are duplicated.')
    ]

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('membership.service.category', string='Category', required=True)
    # membership_product_id = fields.Many2one('product.template','Membership Product')


SERVICE_STATE = [
    ('audit', 'Waiting for Audit'),
    ('paid', 'Waiting for payment'),
    ('available', 'Available'),
    ('expired', 'Expired'),
    ('unpaid', 'Unpaid'),
]

POINTS_TYPE = [
    ('a', 'A'),
    ('b', 'B'),
    ('c', 'C'),
    ('d', 'D'),
]


class ServiceLine(models.Model):
    _name = 'membership.service_line'
    _description = 'membership service line'
    _rec_name = 'membership_server'
    _order = 'create_date,state'

    # 关联的伙伴  购买者的id
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True, required=True)
    # 对应的服务商品
    # membership_server = fields.Many2one(comodel_name='product.product', string='Name', required=True)
    membership_server = fields.Many2one('hotel.services', string='Name', required=True)
    # 分析账户行
    account_invoice_line = fields.Many2one('account.invoice.line', string='Account Invoice line', readonly=True,
                                           ondelete='cascade')
    # 分析账户
    account_invoice_id = fields.Many2one('account.invoice', related='account_invoice_line.invoice_id', string='Invoice',
                                         readonly=True)
    is_use_company = fields.Boolean('Use Company Points', readonly=True)
    use_points_type = fields.Selection(POINTS_TYPE, 'Use Points Type', readonly=True)

    reservation_type = fields.Selection([('invoice','直接预约'),('subscribe','咨询预约')])

    service_price = fields.Float('Price')

    #供应商
    seller_id = fields.Many2one('product.supplierinfo',string="Suplliers")
    start_date = fields.Date(string='Start Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    state = fields.Selection(SERVICE_STATE, 'State', default='audit', store=True,
                             readonly=True)
    use_categ_type = fields.Char('Service Category', readonly=True)
    comments = fields.Text(string='预约备注')

    @api.multi
    def do_submission_done(self):
        for server in self:
            server.state = 'paid'

    #状态的如何不在这里控制，在写入创建的时候控制
    # @api.depends('membership_server')
    # def _compute_info(self):
    #     for server in self:
    #         if server.membership_server:
    #             server.service_price = server.membership_server.list_price
    #             server.use_categ_type = server.membership_server.categ_id.name
    #             if server.membership_server.auto_approval:
    #                 server.state = 'audit'
    #             else:
    #                 server.state = 'paid'

    #扣积分先写死，后期考虑使用模态框来实现
    @api.multi
    def do_service_invoice(self):
        for line in self:
            # 服务
            service_id = self.env['hotel.services'].sudo().search([('id', '=', line.membership_server.id)])

            # 服务的价格
            service_price = line.service_price
            # 查找积分表中是否存在当前类型的积分，优先扣除有有类型的积分
            class_points = self.env['membership.points.lines'].sudo().search(
                [('service_type_id', '=', service_id.categ_id.id), ('partner_id', '=', line.partner_id.id)])
            # 如果存在，则现有扣除当前类型对应的积分
            if class_points:
                class_points.write({
                    "points": class_points.points - service_price
                })
                line.state = 'available'
                return True
            # 没有查找到对应类型的积分，则扣除通用类型和服务类型的积分
            else:
                #服务类型积分
                service_points = self.env['membership.points.lines'].sudo().search(
                    [('partner_id', '=', line.partner_id.id), ('member_type', '=', 'service')])
                #通用类型积分
                currency_points = self.env['membership.points.lines'].sudo().search(
                    [('partner_id', '=', line.partner_id.id), ('member_type', '=', 'currency')])
                if service_points:
                    #如果有服务类型积分
                    #查看服务积分支持哪些类型,先把支持的服务放在list下面
                    service_categ_id = service_id.categ_id.id
                    #存储id
                    bear_type_list = []
                    for bear  in currency_points.product_id.membership_service_type_ids:
                        bear_type_list.append(bear.hotel_service_type_id.id)
                    #如果在支持的类型里，比较积分
                    if service_categ_id in bear_type_list:
                        if service_points.points > service_price:
                            service_points.write({
                                "points": service_points.points - service_price
                            })
                            line.state = 'available'
                            return True
                #以上都不满足，则查看通用类型的积分
                if currency_points:
                    if currency_points.points > service_price:
                        currency_points.write({
                            "points": currency_points.points - service_price
                        })
                        line.state = 'available'
                        return True
            #都不满足，则提醒充值
            raise ValidationError("Insufficient points, please recharge in time")




    @api.multi
    def do_create_services_invoice(self):
        """
        创建会员服务发票
        """
        for partner in self:
            invoice_list = []
            print("partner.partner_id.id")
            print(partner.partner_id.id)
            invoice = self.env['account.invoice'].create({
                'partner_id': partner.partner_id.id,
                'account_id': partner.partner_id.property_account_receivable_id.id,
                'fiscal_position_id': partner.partner_id.property_account_position_id.id,
                'state': 'paid'
            })
            amount = 1
            print("partner.membership_server.name")
            print(partner.membership_server.name)
            line_values = {
                'product_id': partner.membership_server.id,
                'price_unit': amount,
                'invoice_id': invoice.id,
            }
            # create a record in cache, apply onchange then revert back to a dictionnary
            # 在缓存中创建记录，应用onchange然后恢复为字典
            invoice_line = self.env['account.invoice.line'].new(line_values)
            # invoice_line._onchange_product_id()
            # line_values = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
            # line_values['price_unit'] = amount
            # invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
            # invoice_list.append(invoice.id)
            # invoice.compute_taxes()
        return invoice_list



