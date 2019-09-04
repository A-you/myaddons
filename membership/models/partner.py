# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
from datetime import date
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.modules import get_resource_path
from . import membership


#ZW代表已经注册会员，但是没买创客|基本|团体中的一个，他们会应用非会员价
#ZR代表已经注册，也购买了上诉会籍中的一种，享受会员价
LEVEL = [
    (-1,'潜在'),
    (1, 'ZW'),
    (2, 'ZR'),
    (3, 'C'),
]

get_module_resource = get_resource_path


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('membership', 'static/src/img', 'default_image.png')
        print(image_path)
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    # 协同成员
    # 您想要与其成员关联的成员。
    # 意思是获取到其他会员的资格
    associate_member = fields.Many2one('res.partner', string='Associate Member',
                                       help="A member with whom you want to associate your membership."
                                            "It will consider the membership state of the associated member.")

    # 会籍列表
    member_lines = fields.One2many('membership.membership_line', 'partner', string='Membership')
    # 免费会员
    free_member = fields.Boolean(string='Free Member',
                                 help="Select if you want to give free membership.", default=True)
    # 会员金额
    membership_amount = fields.Float(string='Membership Amount', digits=(16, 2),
                                     help='The price negotiated by the partner')
    # 会员状态
    membership_state = fields.Selection(membership.STATE, compute='_compute_membership_state', default='free',
                                        string='Current Membership Status', store=True,
                                        help='It indicates the membership state.\n'
                                             '-Non Member: A partner who has not applied for any membership.\n'
                                             '-Cancelled Member: A member who has cancelled his membership.\n'
                                             '-Old Member: A member whose membership date has expired.\n'
                                             '-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n'
                                             '-Invoiced Member: A member whose invoice has been created.\n'
                                             '-Paying member: A member who has paid the membership fee.')
    # 会员开始日期
    membership_start = fields.Date(compute='_compute_membership_start',
                                   string='Membership Start Date', store=True,
                                   help="Date from which membership becomes active.")
    # 会员结束日期，会员资格保持活跃的日期
    membership_stop = fields.Date(compute='_compute_membership_stop',
                                  string='Membership End Date', store=True,
                                  help="Date until which membership remains active.")


    # 会员取消日期
    membership_cancel = fields.Date(compute='_compute_membership_cancel',
                                    string='Cancel Membership Date', store=True,
                                    help="Date on which membership has been cancelled")

    # 会员等级
    membership_level = fields.Selection(LEVEL, string='Level', default=1)
    #会员标签,购买会籍包可获得
    membership_tag = fields.Many2many('product.template','membership_product_tag_rel','partner_id','product_id',string='Member Title')
    # 会员编号
    membership_numbered = fields.Char(string='Numbered', readonly=True)
    #会员积分列表
    membership_points_lines = fields.One2many('membership.points.lines','partner_id',string='积分列表')

    #会籍服务列表
    membership_server = fields.One2many(comodel_name='membership.service_line', inverse_name='partner_id',
                                        string='Server')

    # 姓：last_name
    # 名：first_name
    # 联络号码：contact_number
    # 手机号码：mobile_number
    # 其他号码：other_number
    # 微信账号：wechat_id
    # 是否从事设计行业：is_design
    # 设计领域服务需求：
    last_name = fields.Char(string='Last Name')
    first_name = fields.Char(string='First Name')
    other_phone = fields.Char(string='Other Number')
    wechat = fields.Char(string='WeChat ID')
    is_design = fields.Boolean(string='Is Design')
    come_from = fields.Char(string='Come From')
    #工作类型
    job_type = fields.Char(string='Job Type')
    # 公司
    # 建立时间
    company_creation_date = fields.Char(string='Creation Date')
    area = fields.Char(string='Area')
    # 展示图片
    show_image1 = fields.Binary(string='Show Image1', attachment=True)
    show_image2 = fields.Binary(string='Show Image2', attachment=True)
    show_image3 = fields.Binary(string='Show Image3', attachment=True)
    # show_image1_url = fields.Char(string='Show Image1 URL', compute="_compute_show_image1_url", store=True)
    # show_image2_url = fields.Char(string='Show Image2 URL', compute="_compute_show_image2_url", store=True)
    # show_image3_url = fields.Char(string='Show Image3 URL', compute="_compute_show_image3_url", store=True)
    # image_url = fields.Char(string='Avatar URL', compute="_compute_image_url", store=True)

    show_image1_url = fields.Char(string='Show Image1 URL', store=True)
    show_image2_url = fields.Char(string='Show Image2 URL', store=True)
    show_image3_url = fields.Char(string='Show Image3 URL', store=True)
    image_url = fields.Char(string='Avatar URL', store=True)
    # 重写覆盖
    name = fields.Char(index=True, readonly=False)
    phone = fields.Char(string='Contact Number')
    mobile = fields.Char(string='Mobile Number')
    title = fields.Char()

    # 1，在設計行業工作年份
    # 2，密碼
    # 3，身份證號碼
    # 4，身份證明類別

    design_working_years = fields.Float(string='Design Working Years')
    password = fields.Char(string='Password')
    id_number = fields.Char(string='ID Number')
    id_type = fields.Char(string='ID Type')
    # 业务类型
    # facebook账户
    # instagram账户
    # 其他账户
    # 员工数目
    # 服务领域

    facebook_account = fields.Char(string='Facebook Account')
    instagram_account = fields.Char(string='Instagram Account')
    other_account = fields.Char(string='Other Account')
    employee_number = fields.Integer(string='Employee Number')
    service_field = fields.Many2many('res.partner.service.field', column1='partner_id',
                                     column2='service_field_id', string='Service Field')
    # 微博账号
    # linkedin账号
    # twitter账号
    # Google+账号
    # pinterest账号
    weibo_account = fields.Char(string='WeiBo Account')
    linkedin_account = fields.Char(string='Linkedin Account')
    twitter_account = fields.Char(string='Twitter Account')
    google_account = fields.Char(string='Google+ Account')
    pinterest_account = fields.Char(string='Pinterest Account')


    # 添加中英文名
    en_last_name = fields.Char(string='English Last Name')
    en_first_name = fields.Char(string='English First Name')

    #微服务系统唯一表示符
    ocean_platform_id = fields.Char(string='Microservices Account')

    #公司的唯一表示符
    uniform_social_credit_code = fields.Char(string='BR code')


    #多个公司或多个人
    personal_or_company = fields.Many2many('res.partner','personal_or_company_rel','current_id','relation_id',string='Personal Company')


    #sql约束微服务识别号唯一
    _sql_constraints = [(
        'partner_ocean_platform_id_unique',
        'UNIQUE (ocean_platform_id, create_uid)',
        'partner ocean_platform_id with create_uid is existed！'
    )]

    # @api.model
    # def create(self, vals):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     return super(Partner, self).create(vals)
    @api.model
    def create(self, vals):
        # print(vals)
        if not vals.get('is_company'):
            # 个人
            if vals.get('first_name') and vals.get('last_name'):
                vals['name'] = '%s %s' % (vals.get('first_name') or '', vals.get('last_name') or '')
            elif not vals.get('first_name') and vals.get('last_name'):
                vals['name'] = '%s' % vals.get('last_name') or ''
            elif vals.get('first_name') and not vals.get('last_name'):
                vals['name'] = '%s' % vals.get('last_name') or ''
            else:
                raise ValueError("Missing first_name or last_name")
        else:
            # 公司
            if not vals.get('name'):
                raise ValueError('Missing name')
        return super(Partner, self).create(vals)

    @api.multi
    @api.depends('show_image1')
    def _compute_show_image1_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in self:
            line.show_image1_url = '%s/web/image?model=res.partner&id=%s&field=show_image1' % (base_url, line.id)

    @api.multi
    @api.depends('show_image2')
    def _compute_show_image2_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in self:
            line.show_image2_url = '%s/web/image?model=res.partner&id=%s&field=show_image2' % (base_url, line.id)

    @api.multi
    @api.depends('show_image3')
    def _compute_show_image3_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in self:
            line.show_image3_url = '%s/web/image?model=res.partner&id=%s&field=show_image3' % (base_url, line.id)

    @api.multi
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in self:
            line.image_url = '%s/web/image?model=res.partner&id=%s&field=image' % (base_url, line.id)

    # @api.multi
    # @api.depends('membership_points_a', 'membership_points_b', 'membership_points_c', 'membership_points_d')
    # def _compute_membership_points(self):
    #     for line in self:
    #         line.membership_points = line.membership_points_a + line.membership_points_b + \
    #                                  line.membership_points_c + line.membership_points_d


    @api.multi
    @api.onchange('first_name', 'last_name')
    def _compute_name(self):
        for partner in self:
            if not partner.is_company:
                partner.name = '%s %s' % (partner.first_name or '', partner.last_name or '')

    @api.multi
    def write(self, vals):
        # 生成会员编号
        if not self.membership_numbered:
            vals['membership_numbered'] = self.env['ir.sequence'].next_by_code(
                'membership.numbered') or ''
        return super(Partner, self).write(vals)

    @api.depends('member_lines.account_invoice_line.invoice_id.state',
                 'member_lines.account_invoice_line.invoice_id.invoice_line_ids',
                 'member_lines.account_invoice_line.invoice_id.payment_ids',
                 'member_lines.account_invoice_line.invoice_id.payment_move_line_ids',
                 'member_lines.account_invoice_line.invoice_id.partner_id',
                 # 'free_member',
                 'member_lines.date_to', 'member_lines.date_from',
                 'associate_member.membership_state')
    def _compute_membership_state(self):
        # 自动计算会员状态
        values = self._membership_state()
        for partner in self:
            partner.membership_state = values[partner.id]

    @api.depends('member_lines.account_invoice_line.invoice_id.state',
                 'member_lines.account_invoice_line.invoice_id.invoice_line_ids',
                 'member_lines.account_invoice_line.invoice_id.payment_ids',
                 # 'free_member',
                 'member_lines.date_to', 'member_lines.date_from', 'member_lines.date_cancel',
                 'membership_state',
                 'associate_member.membership_state')
    def _compute_membership_start(self):
        """Return  date of membership
            自动计算开始日期
        """
        for partner in self:
            partner.membership_start = self.env['membership.membership_line'].search([
                ('partner', '=', partner.associate_member.id or partner.id), ('date_cancel', '=', False)
            ], limit=1, order='date_from').date_from

    @api.depends('member_lines.account_invoice_line.invoice_id.state',
                 'member_lines.account_invoice_line.invoice_id.invoice_line_ids',
                 'member_lines.account_invoice_line.invoice_id.payment_ids',
                 # 'free_member',
                 'member_lines.date_to', 'member_lines.date_from', 'member_lines.date_cancel',
                 'membership_state',
                 'associate_member.membership_state')
    def _compute_membership_stop(self):
        # 自动计算会员到期时间
        # 触发条件：
        # 会员行的发票状态
        # 发票的发票行改变
        # 发票的付款改变
        # 免费会员勾选改变
        # 会员行的结束日期、开始日期、取消日期改变
        # 会员状态改变
        # 协同会员改变
        # MemberLine = self.env['membership.membership_line']
        for partner in self:
            # 取最新的会员行到期时间，设置到最新的会员到期时间
            partner.membership_stop = self.env['membership.membership_line'].search([
                ('partner', '=', partner.associate_member.id or partner.id), ('date_cancel', '=', False)
            ], limit=1, order='date_to desc').date_to

    @api.depends('member_lines.account_invoice_line.invoice_id.state',
                 'member_lines.account_invoice_line.invoice_id.invoice_line_ids',
                 'member_lines.account_invoice_line.invoice_id.payment_ids',
                 # 'free_member',
                 'member_lines.date_to', 'member_lines.date_from', 'member_lines.date_cancel',
                 'membership_state',
                 'associate_member.membership_state')
    def _compute_membership_cancel(self):
        # 自动计算取消会员日期
        # 触发条件：
        # 发票状态改变
        # 是否免费会员
        for partner in self:
            # 如果会员状态为取消，则设置会员的最新取消时间
            if partner.membership_state == 'canceled':
                partner.membership_cancel = self.env['membership.membership_line'].search([
                    ('partner', '=', partner.id)
                ], limit=1, order='date_cancel').date_cancel
            else:
                # 如果会员状态不是取消，则清空会员取消时间
                partner.membership_cancel = False

    def _membership_state(self):
        """返回会员身份"""
        """This Function return Membership State For Given Partner. """
        res = {}
        # 获取今天时间
        today = fields.Date.today()
        for partner in self:
            # res[partner.id] = 'none'
            res[partner.id] = 'free'
            # 如果会员取消日期存在，且 今天大于会员取消日期
            if partner.membership_cancel and today > partner.membership_cancel:
                # 则设置该会员为免费
                res[partner.id] = 'free'
                # res[partner.id] = 'free' if partner.free_member else 'canceled'
                continue
            # 如果存在会员到期时间，并且今天大于到期时间（即会员已经过期）
            if partner.membership_stop and today > partner.membership_stop:
                res[partner.id] = 'old'
                # res[partner.id] = 'free' if partner.free_member else 'old'
                continue
            # 如果存在协同会员，将他状态设置成与协同会员一样
            if partner.associate_member:
                res_state = partner.associate_member._membership_state()
                res[partner.id] = res_state[partner.associate_member.id]
                continue

            s = 4
            # 如果存在购买会员记录
            if partner.member_lines:
                # 遍历购买会员记录
                for mline in partner.member_lines:
                    # 如果会员购买记录的结束时间大于今天，会员购买记录的开始时间小于今天。（如果还没过期）
                    if (mline.date_to or date.min) >= today >= (mline.date_from or date.min):
                        # 如果会员购买记录的购买用户等于当前用户
                        if mline.account_invoice_line.invoice_id.partner_id == partner:
                            # 存储这个发票的状态
                            mstate = mline.account_invoice_line.invoice_id.state
                            # 如果已经支付
                            if mstate == 'paid':
                                s = 0
                                inv = mline.account_invoice_line.invoice_id
                                for ml in inv.payment_move_line_ids:
                                    if any(ml.invoice_id.filtered(lambda inv: inv.type == 'out_refund')):
                                        s = 2
                                break
                            elif mstate == 'open' and s != 0:
                                s = 1
                            elif mstate == 'cancel' and s != 0 and s != 1:
                                s = 2
                            elif mstate == 'draft' and s != 0 and s != 1:
                                s = 3
                # 如果还没有做购买记录
                if s == 4:
                    for mline in partner.member_lines:
                        # 如果会员过期,设置为过期会员，否则为空
                        if (mline.date_from or date.min) < today and (mline.date_to or date.min) < today and (
                                mline.date_from or date.min) <= (
                                mline.date_to or date.min) and mline.account_invoice_line and mline.account_invoice_line.invoice_id.state == 'paid':
                            s = 5
                        else:
                            s = 6
                if s == 0:
                    res[partner.id] = 'paid'
                elif s == 1:
                    res[partner.id] = 'invoiced'
                elif s == 2:
                    res[partner.id] = 'canceled'
                elif s == 3:
                    res[partner.id] = 'waiting'
                elif s == 5:
                    res[partner.id] = 'old'
                elif s == 6:
                    res[partner.id] = 'free'
                    # res[partner.id] = 'none'
            # if partner.free_member and s != 0:
            #     res[partner.id] = 'free'
        return res

    @api.one
    @api.constrains('associate_member')
    # 检查协同会员
    def _check_recursion_associate_member(self):
        level = 100
        while self:
            self = self.associate_member
            if not level:
                # 您无法创建递归关联成员
                raise ValidationError(_('You cannot create recursive associated members.'))
            level -= 1

    @api.model
    def _cron_update_membership(self):
        partners = self.search([('membership_state', 'in', ['invoiced', 'paid'])])
        # mark the field to be recomputed, and recompute it
        partners._recompute_todo(self._fields['membership_state'])
        self.recompute()


    #创建一个会籍的发票
    @api.multi
    def create_membership_invoice(self, product_id=None, datas=None):
        """ Create Customer Invoice of Membership for partners.为合作伙伴创建会员的客户发票
        @param datas: datas has dictionary value which consist Id of Membership product and Cost Amount of Membership.
                      具有字典值，包括会员产品的Id和会员的成本金额。
                      datas = {'membership_product_id': None, 'amount': None}
        """
        product_id = product_id or datas.get('membership_product_id')    #产品id，对应选择的会员产品id
        amount = datas.get('amount', 0.0)    #对应会员产品价格
        personal_id = datas.get('personal_id',2)  #购买人，前端购买者。
        invoice_list = []
        for partner in self:
            addr = partner.address_get(['invoice'])
            # 免费会员不用购买会员
            # if partner.free_member:
            #     raise UserError(_("Partner is a free Member."))
            # 合作伙伴没有地址来制作发票。
            print(addr)
            if not addr.get('invoice', False):
                raise UserError(_("Partner doesn't have an address to make the invoice."))
            invoice = self.env['account.invoice'].create({
                'partner_id': partner.id,
                'personal_id': int(personal_id),
                'account_id': partner.property_account_receivable_id.id,
                'fiscal_position_id': partner.property_account_position_id.id
            })
            line_values = {
                'product_id': product_id,
                'price_unit': amount,
                'invoice_id': invoice.id,
            }
            # create a record in cache, apply onchange then revert back to a dictionnary
            # 在缓存中创建记录，应用onchange然后恢复为字典
            invoice_line = self.env['account.invoice.line'].new(line_values)
            invoice_line._onchange_product_id()
            line_values = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
            line_values['price_unit'] = amount
            invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
            invoice_list.append(invoice.id)
            invoice.compute_taxes()
        return invoice_list

    @api.multi
    def create_membership_services_invoice(self, product_ids=None, datas=None):
        """
        创建会员服务发票
        """
        # product_ids = product_ids or datas.get('membership_services_product_ids')
        product_ids = product_ids or datas.get('membership_services_ids')
        invoice_list = []  # 发票列表
        for partner in self:
            addr = partner.address_get(['invoice'])
            print(addr)
            # 非会员不能购买
            # if partner.membership_state == 'paid':
            #     raise UserError(_("Only paid members can purchase membership services."))
            # 合作伙伴没有地址来制作发票。
            if not addr.get('invoice', False):
                raise UserError(_("Partner doesn't have an address to make the invoice."))
            # 创建发票对象
            invoice = self.env['account.invoice'].create({
                'partner_id': partner.id,
                'use_points_wallet': datas.get('use_points_wallet', False),
                'account_id': partner.property_account_receivable_id.id,
                'fiscal_position_id': partner.property_account_position_id.id
            })
            # 添加商品进发票
            print("product_ads",product_ids)
            for obj in product_ids:
                product_id = obj.product_id
                print('product_id')
                print(obj.product_id)
                print(obj.name)
                line_values = {
                    'product_id': product_id.id,
                    'price_unit': product_id.list_price,
                    'invoice_id': invoice.id,
                    'use_points_wallet': datas.get('use_points_wallet', False),
                    # 'use_points_type': 'a',
                }
                print(line_values)
                invoice_line = self.env['account.invoice.line'].new(line_values)  # 在缓存中创建记录，然后再缓存中创建字典
                invoice_line._onchange_product_id()  # 执行当商品id改变，以获得其他值字段自动填入
                line_values = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
                # line_values['price_unit'] = amount
                invoice.write({
                    'invoice_line_ids': [(0, 0, line_values)],
                })
            invoice_list.append(invoice.id)
            invoice.compute_taxes()
        return invoice_list
        # return True


class ServiceField(models.Model):
    _name = 'res.partner.service.field'
    _description = '业务性质/服务领域'

    name = fields.Char(string='Name', required=True, translate=True)
    parent_id = fields.Many2one('res.partner.service.field', string='Parent Category', index=True,
                                ondelete='cascade')
    child_ids = fields.One2many('res.partner.service.field', 'parent_id', string='Child Field')
    active = fields.Boolean(string='Active', default=True,
                            help="The active field allows you to hide the category without removing it.")

    web_open = fields.Boolean(string='公开',help='是否公开到前端页面，前端页面指的是否允许通过api访问的')
