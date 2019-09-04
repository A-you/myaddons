# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import ValidationError, UserError
import pytz

is_log = True


def my_log(text):
    if is_log:
        print(text)


def hour_range_list(start, end):
    return list(range(start, end + 1))


def utc2bj(utc_time):
    return utc_time + timedelta(hours=8)


# 账单
class HotelFolio(models.Model):
    _inherit = 'hotel.folio'
    _order = 'reservation_id desc'

    reservation_id = fields.Many2one('hotel.reservation',
                                     string='Reservation Id')

    @api.multi
    def write(self, vals):
        context = dict(self._context)
        if not context:
            context = {}
        context.update({'from_reservation': True})
        res = super(HotelFolio, self).write(vals)
        reservation_line_obj = self.env['hotel.room.reservation.line']

        for folio_obj in self:
            my_log('111111111111111111111')
            if folio_obj.reservation_id and folio_obj.hotel_invoice_id.state == 'paid':

                for reservation in folio_obj.reservation_id:
                    reservation_obj = (reservation_line_obj.search
                                       ([('reservation_id', '=',
                                          reservation.id)]))
                    my_log(reservation_obj)
                    if len(reservation_obj) == 1:
                        for line_id in reservation.reservation_line:
                            line_id = line_id.reserve
                            for room_id in line_id:
                                vals = {'room_id': room_id.id,
                                        'check_in': folio_obj.checkin_date,
                                        'check_out': folio_obj.checkout_date,
                                        'state': 'assigned',
                                        'reservation_id': reservation.id,
                                        }
                                reservation_obj.write(vals)
        return res

    @api.multi
    def action_done(self):
        # 账单完成后，将预约变成完成
        super(HotelFolio, self).action_done()

        reservation_line_obj = self.env['hotel.room.reservation.line']
        for folio_obj in self:
            my_log('111111111111111111111')
            if folio_obj.reservation_id and folio_obj.hotel_invoice_id.state == 'paid':

                for reservation in folio_obj.reservation_id:
                    reservation_obj = (reservation_line_obj.search
                                       ([('reservation_id', '=',
                                          reservation.id)]))
                    my_log(reservation_obj)
                    if len(reservation_obj) == 1:
                        for line_id in reservation.reservation_line:
                            line_id = line_id.reserve
                            for room_id in line_id:
                                vals = {'room_id': room_id.id,
                                        'check_in': folio_obj.checkin_date,
                                        'check_out': folio_obj.checkout_date,
                                        'state': 'assigned',
                                        'reservation_id': reservation.id,
                                        }
                                reservation_obj.write(vals)
                self.reservation_id.state = 'done'
            else:
                raise ValidationError('Unpaid')

    # @api.multi
    # def action_cancel(self):
    #     '''
    #     @param self: object pointer
    #     '''
    #     self.reservation_id.state = 'done'
    #     super(HotelFolio, self).action_done()


class HotelFolioLineExt(models.Model):
    _inherit = 'hotel.folio.line'

    @api.onchange('checkin_date', 'checkout_date')
    def on_change_checkout(self):
        res = super(HotelFolioLineExt, self).on_change_checkout()
        hotel_room_obj = self.env['hotel.room']
        avail_prod_ids = []
        hotel_room_ids = hotel_room_obj.search([])
        for room in hotel_room_ids:
            assigned = False
            for line in room.room_reservation_line_ids:
                if line.status != 'cancel':
                    if (self.checkin_date <= line.check_in <=
                        self.checkout_date) or (self.checkin_date <=
                                                line.check_out <=
                                                self.checkout_date):
                        assigned = True
                    elif (line.check_in <= self.checkin_date <=
                          line.check_out) or (line.check_in <=
                                              self.checkout_date <=
                                              line.check_out):
                        assigned = True
            if not assigned:
                avail_prod_ids.append(room.product_id.id)
        return res

    @api.multi
    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        Update Hotel Room Reservation line history"""
        reservation_line_obj = self.env['hotel.room.reservation.line']
        room_obj = self.env['hotel.room']
        prod_id = vals.get('product_id') or self.product_id.id
        chkin = vals.get('checkin_date') or self.checkin_date
        chkout = vals.get('checkout_date') or self.checkout_date
        is_reserved = self.is_reserved
        if prod_id and is_reserved:
            prod_domain = [('product_id', '=', prod_id)]
            prod_room = room_obj.search(prod_domain, limit=1)
            if (self.product_id and self.checkin_date and self.checkout_date):
                old_prd_domain = [('product_id', '=', self.product_id.id)]
                old_prod_room = room_obj.search(old_prd_domain, limit=1)
                if prod_room and old_prod_room:
                    # Check for existing room lines.
                    srch_rmline = [('room_id', '=', old_prod_room.id),
                                   ('check_in', '=', self.checkin_date),
                                   ('check_out', '=', self.checkout_date),
                                   ]
                    rm_lines = reservation_line_obj.search(srch_rmline)
                    if rm_lines:
                        rm_line_vals = {'room_id': prod_room.id,
                                        'check_in': chkin,
                                        'check_out': chkout}
                        rm_lines.write(rm_line_vals)
        return super(HotelFolioLineExt, self).write(vals)


# 空间预定单（针对客户）
class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = 'reservation_no desc'
    _inherit = ['mail.thread']

    # 预定编号
    reservation_no = fields.Char('Reservation No', readonly=True)
    # 订单日期
    date_order = fields.Datetime('Date Ordered', readonly=True, required=True,
                                 index=True,
                                 default=(lambda *a: time.strftime(dt)))

    # 仓库
    warehouse_id = fields.Many2one('stock.warehouse', 'Space Provider', readonly=True,
                                   index=True,
                                   required=True, default=1,
                                   states={'draft': [('readonly', False)]})
    # 伙伴
    partner_id = fields.Many2one('res.partner', 'Guest Name', readonly=True,
                                 index=True,
                                 required=True,
                                 states={'draft': [('readonly', False)]})
    # 当前预定的价格表
    pricelist_id = fields.Many2one('product.pricelist', 'Scheme',
                                   required=True, readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   help="Pricelist for current reservation.")

    # 当前预订的发票地址
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address',
                                         readonly=True,
                                         states={'draft':
                                                     [('readonly', False)]},
                                         help="Invoice address for current reservation.")

    # 请求订单或报价的联系人的姓名和地址
    partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
                                       readonly=True,
                                       states={'draft':
                                                   [('readonly', False)]},
                                       help="The name and address of the contact that requested the order or quotation.")
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          readonly=True,
                                          states={'draft':
                                                      [('readonly', False)]},
                                          help="Delivery address"
                                               "for current reservation. ")
    # 入住时间
    checkin = fields.Datetime('Expected-Date-Arrival', required=True,
                              readonly=True,
                              states={'draft': [('readonly', False)]})

    # 退订时间
    checkout = fields.Datetime('Expected-Date-Departure', required=True,
                               readonly=True,
                               states={'draft': [('readonly', False)]})

    # 成人数量
    adults = fields.Integer('Number of people', readonly=True,
                            states={'draft': [('readonly', False)]},
                            help='List of adults there in guest list. ')
    # adults = fields.Integer('Adults', readonly=True,
    #                         states={'draft': [('readonly', False)]},
    #                         help='List of adults there in guest list. ')
    # 小孩数量
    children = fields.Integer('Children', readonly=True,
                              states={'draft': [('readonly', False)]},
                              help='Number of children there in guest list.')

    # 预定空间列表
    reservation_line = fields.One2many('hotel_reservation.line', 'line_id',
                                       'Reservation Line',
                                       help='space reservation details.',
                                       readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       )
    # 状态：草案、确认、取消、完成
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('cancel', 'Cancel'), ('done', 'Done')],
                             'State', readonly=True,
                             default=lambda *a: 'draft')

    # 账单
    folio_id = fields.Many2many('hotel.folio', 'hotel_folio_reservation_rel',
                                'order_id', 'invoice_id', string='Folio')
    new_folio_id = fields.Many2one(comodel_name='hotel.folio')
    # 账单号
    no_of_folio = fields.Integer('Folio', compute="_compute_folio_id")
    dummy = fields.Datetime('Dummy')

    company_id = fields.Many2one('res.company', string='Company')

    # 新增 partner_order_id
    # 联系人称谓：title
    # 联系人姓：first_name
    # 名：last_name
    # 联系人电话：phone
    partner_title = fields.Char(string='称谓', compute='_compute_partner', readonly=True, store=True)
    partner_first_name = fields.Char(string='First Name', compute='_compute_partner', readonly=True, store=True)
    partner_last_name = fields.Char(string='Last Name', compute='_compute_partner', readonly=True, store=True)
    partner_phone = fields.Char(string='Contact Number', compute='_compute_partner', readonly=True, store=True)
    partner_image_url = fields.Char(string='Avatar URL', compute='_compute_partner', readonly=True, store=True)
    remark = fields.Text(string='Remark')
    company_name = fields.Char(string='Company Name', compute='_compute_partner', store=True)

    @api.multi
    @api.depends('partner_order_id')
    def _compute_partner(self):
        for line in self:
            if line.partner_order_id:
                line.partner_title = line.partner_order_id.title
                line.partner_first_name = line.partner_order_id.first_name
                line.partner_last_name = line.partner_order_id.last_name
                line.partner_phone = line.partner_order_id.phone
                line.partner_image_url = line.partner_order_id.image_url
                if line.partner_order_id.parent_id:
                    line.company_name = line.partner_order_id.parent_id.name

    @api.multi
    def _compute_folio_id(self):
        folio_list = []
        for res in self:
            for folio in res.folio_id:
                folio_list.append(folio.id)
            folio_len = len(folio_list)
            res.no_of_folio = folio_len
        return folio_len

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for reserv_rec in self:
            if reserv_rec.state != 'draft':
                raise ValidationError(_('You cannot delete Reservation in %s\
                                         state.') % (reserv_rec.state))
        return super(HotelReservation, self).unlink()

    @api.multi
    def copy(self):
        ctx = dict(self._context) or {}
        ctx.update({'duplicate': True})
        return super(HotelReservation, self.with_context(ctx)).copy()

    @api.constrains('reservation_line', 'adults', 'children')
    def check_reservation_rooms(self):
        '''
        This method is used to validate the reservation_line.
        -----------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        '''
        ctx = dict(self._context) or {}
        for reservation in self:
            cap = 0
            for rec in reservation.reservation_line:
                if len(rec.reserve) == 0:
                    raise ValidationError(_(
                        'Please Select Rooms For Reservation.'))
                for room in rec.reserve:
                    cap += room.capacity
            if not ctx.get('duplicate'):
                if (reservation.adults + reservation.children) > cap:
                    raise ValidationError(_(
                        'Space Capacity Exceeded \n'
                        ' Please Select Spaces According to'
                        ' Members Accomodation.'))
            if reservation.adults <= 0:
                # raise ValidationError(_('Adults must be more than 0'))
                pass

    @api.constrains('checkin', 'checkout')
    def check_in_out_dates(self):
        """
        When date_order is less then check-in date or
        Checkout date should be greater than the check-in date.
        """
        if self.checkout and self.checkin:
            if self.checkin < self.date_order:
                raise ValidationError(_('Check-in date should be greater than \
                                         the current date.'))
            if self.checkout < self.checkin:
                raise ValidationError(_('Check-out date should be greater \
                                         than Check-in date.'))

    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state reservations on the menu badge.
         """
        return self.search_count([('state', '=', 'draft')])

    @api.onchange('checkout', 'checkin')
    def on_change_checkout(self):
        '''
        When you change checkout or checkin update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        '''
        checkout_date = time.strftime(dt)
        checkin_date = time.strftime(dt)
        if not (checkout_date and checkin_date):
            return {'value': {}}
        delta = timedelta(days=1)
        dat_a = time.strptime(checkout_date, dt)[:5]
        addDays = datetime(*dat_a) + delta
        self.dummy = addDays.strftime(dt)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        '''
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.partner_order_id = False
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice',
                                                'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if not vals:
            vals = {}
        vals['reservation_no'] = self.env['ir.sequence']. \
                                     next_by_code('hotel.reservation') or 'New'
        return super(HotelReservation, self).create(vals)

    @api.multi
    def check_overlap(self, date1, date2):
        date2 = datetime.strptime(date2, '%Y-%m-%d')
        date1 = datetime.strptime(date1, '%Y-%m-%d')
        delta = date2 - date1
        return set([date1 + timedelta(days=i) for i in range(delta.days + 1)])

    @api.multi
    def confirmed_reservation(self):
        """
        This method create a new record set for hotel room reservation line
        此方法为酒店房间预订行创建新记录集
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel room reservation line.
        """
        reservation_line_obj = self.env['hotel.room.reservation.line']
        vals = {}
        for reservation in self:
            reserv_checkin = reservation.checkin
            reserv_checkout = reservation.checkout
            room_bool = False
            # 遍历预约的空间
            for line_id in reservation.reservation_line:
                # 遍历空间的预约单
                for room_id in line_id.reserve:
                    # 如果这个空间有预约单
                    if room_id.room_reservation_line_ids:
                        # 遍历这个空间的已经确认和完成的预约单，并且属于这个空间
                        # for reserv in room_id.room_reservation_line_ids.search([('status', 'in', ('confirm', 'done')),('room_id', '=', room_id.id)]):
                        for reserv in room_id.room_reservation_line_ids.search(
                                [('status', 'in', ('done',)), ('room_id', '=', room_id.id)]):
                            # 获取这个预约单的入住和退房时间
                            check_in = reserv.check_in
                            check_out = reserv.check_out
                            # 判断该预约单与该空间已经确认和完成的预约单是否有重叠时间
                            # 这预约单的入住时间 <= 本次预约的入住时间 <= 本次预约的退房时间
                            if check_in <= reserv_checkin <= check_out:
                                room_bool = True
                            if check_in <= reserv_checkout <= check_out:
                                room_bool = True
                            if reserv_checkin <= check_in and \
                                    reserv_checkout >= check_out:
                                room_bool = True
                            mytime = "%Y-%m-%d"
                            r_checkin = (reservation.checkin).date()
                            r_checkin = r_checkin.strftime(mytime)
                            r_checkout = (reservation.checkout).date()
                            r_checkout = r_checkout.strftime(mytime)
                            check_intm = (reserv.check_in).date()
                            check_outtm = (reserv.check_out).date()
                            check_intm = check_intm.strftime(mytime)
                            check_outtm = check_outtm.strftime(mytime)
                            range1 = [r_checkin, r_checkout]
                            range2 = [check_intm, check_outtm]
                            overlap_dates = self.check_overlap(*range1) \
                                            & self.check_overlap(*range2)
                            overlap_dates = [datetime.strftime(dates,
                                                               '%d/%m/%Y') for
                                             dates in overlap_dates]
                            if room_bool:
                                # 您尝试使用此预订期间已预留的房间确认预订。 重叠日期是
                                raise ValidationError(_('You tried to Confirm '
                                                        'Reservation with room'
                                                        ' those already '
                                                        'reserved in this '
                                                        'Reservation Period. '
                                                        'Overlap Dates are '
                                                        '%s') % overlap_dates)
                            else:
                                # 没有重叠时间unassigned
                                self.state = 'confirm'
                                vals = {'room_id': room_id.id,
                                        'check_in': reservation.checkin,
                                        'check_out': reservation.checkout,
                                        # 'state': 'occupied',
                                        'state': 'unassigned',
                                        'reservation_id': reservation.id,
                                        }
                                # room_id.write({'isroom': False, 'status': 'occupied'})
                                room_id.write({'isroom': False, 'status': 'assigned'})
                        else:
                            # 确认
                            self.state = 'confirm'
                            vals = {'room_id': room_id.id,
                                    'check_in': reservation.checkin,
                                    'check_out': reservation.checkout,
                                    'state': 'unassigned',
                                    'reservation_id': reservation.id,
                                    }
                            # room_id.write({'isroom': False, 'status': 'occupied'})
                            room_id.write({'isroom': False, 'status': 'assigned'})
                    else:
                        # 确认
                        self.state = 'confirm'
                        vals = {'room_id': room_id.id,
                                'check_in': reservation.checkin,
                                'check_out': reservation.checkout,
                                'state': 'unassigned',
                                'reservation_id': reservation.id,
                                }
                        # room_id.write({'isroom': False, 'status': 'occupied'})
                        room_id.write({'isroom': False, 'status': 'assigned'})
                    reservation_line_obj.create(vals)
                    if self.state == 'confirm':
                        self.create_folio()
        return True

    @api.multi
    def cancel_reservation(self):
        """
        This method cancel record set for hotel room reservation line
        ------------------------------------------------------------------
        @param self: The object pointer
        @return: cancel record set for hotel room reservation line.
        """
        room_res_line_obj = self.env['hotel.room.reservation.line']
        hotel_res_line_obj = self.env['hotel_reservation.line']
        self.state = 'cancel'
        room_reservation_line = room_res_line_obj.search([('reservation_id',
                                                           'in', self.ids)])
        room_reservation_line.write({'state': 'unassigned'})
        room_reservation_line.unlink()
        reservation_lines = hotel_res_line_obj.search([('line_id',
                                                        'in', self.ids)])
        for reservation_line in reservation_lines:
            reservation_line.reserve.write({'isroom': True,
                                            'status': 'available'})
        return True

    @api.multi
    def set_to_draft_reservation(self):
        self.state = 'draft'
        return True

    @api.multi
    def action_send_reservation_mail(self):
        '''
        This function opens a window to compose an email,
        template message loaded by default.
        @param self: object pointer
        '''
        self.ensure_one()
        try:
            template_id = self.env.ref('hotel_reservation.\
            email_template_hotel_reservation').id
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env.ref('mail.\
            email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hotel.reservation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def reservation_reminder_24hrs(self):
        """
        This method is for scheduler
        every 1day scheduler will call this method to
        find all tomorrow's reservations.
        ----------------------------------------------
        @param self: The object pointer
        @return: send a mail
        """
        now_str = time.strftime(dt)
        now_date = datetime.strptime(now_str, dt)
        ir_model_data = self.env['ir.model.data']
        template_id = (ir_model_data.get_object_reference
        ('hotel_reservation',
         'mail_template_reservation_reminder_24hrs')[1])
        template_rec = self.env['mail.template'].browse(template_id)
        for reserv_rec in self.search([]):
            checkin_date = reserv_rec.checkin
            difference = relativedelta(now_date, checkin_date)
            if (difference.days == -1 and reserv_rec.partner_id.email and
                    reserv_rec.state == 'confirm'):
                template_rec.send_mail(reserv_rec.id, force_send=True)
        return True

    @api.multi
    def create_folio(self):
        """
        This method is for create new hotel folio.
        这个方法是用于创建一个新的账单
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        hotel_folio_obj = self.env['hotel.folio']
        room_obj = self.env['hotel.room']
        for reservation in self:
            folio_lines = []
            checkin_date = reservation['checkin']
            checkout_date = reservation['checkout']
            if not self.checkin < self.checkout:
                raise ValidationError(_('Checkout date should be greater \
                                         than the Check-in date.'))
            duration_vals = (self.onchange_check_dates
                             (checkin_date=checkin_date,
                              checkout_date=checkout_date, duration=False))
            duration = duration_vals.get('duration') or 0.0
            folio_vals = {
                'date_order': reservation.date_order,
                'warehouse_id': reservation.warehouse_id.id,
                'partner_id': reservation.partner_id.id,
                'pricelist_id': reservation.pricelist_id.id,
                'partner_invoice_id': reservation.partner_invoice_id.id,
                'partner_shipping_id': reservation.partner_shipping_id.id,
                'checkin_date': reservation.checkin,
                'checkout_date': reservation.checkout,
                'duration': duration,
                'reservation_id': reservation.id,
                'service_lines': reservation['folio_id']
            }
            for line in reservation.reservation_line:
                for r in line.reserve:
                    folio_lines.append((0, 0, {
                        'checkin_date': checkin_date,
                        'checkout_date': checkout_date,
                        'product_id': r.product_id and r.product_id.id,
                        'name': reservation['reservation_no'],
                        'price_unit': r.list_price,
                        'product_uom_qty': duration,
                        'is_reserved': True}))
                    res_obj = room_obj.browse([r.id])
                    res_obj.write({'status': 'occupied', 'isroom': False})
            folio_vals.update({'room_lines': folio_lines})
            folio = hotel_folio_obj.create(folio_vals)
            if folio:
                for rm_line in folio.room_lines:
                    rm_line.product_id_change()
            self._cr.execute('insert into hotel_folio_reservation_rel'
                             '(order_id, invoice_id) values (%s,%s)',
                             (reservation.id, folio.id))
            # reservation.write(new_folio_id = folio)
            reservation.write({
                'new_folio_id': folio.id,
            })
            # 确认账单销售
            folio.action_confirm()
            # 创建发票
            invoice_id = folio.action_invoice_create()
            print(invoice_id)
            if invoice_id:
                invoice = self.env['account.invoice'].sudo().browse(int(invoice_id))
                print(invoice)
                if invoice:
                    invoice = invoice[0]
                    invoice.action_invoice_open()
            # self.state = 'done'
        return True

    @api.multi
    def onchange_check_dates(self, checkin_date=False, checkout_date=False,
                             duration=False):
        '''
        This method gives the duration between check in checkout if
        customer will leave only for some hour it would be considers
        as a whole day. If customer will checkin checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        '''
        value = {}
        configured_addition_hours = 0
        wc_id = self.warehouse_id
        whcomp_id = wc_id or wc_id.company_id
        if whcomp_id:
            configured_addition_hours = wc_id.company_id.additional_hours
        duration = 0
        if checkin_date and checkout_date:
            dur = checkout_date - checkin_date
            duration = dur.days + 1
            if configured_addition_hours > 0:
                additional_hours = abs((dur.seconds / 60))
                if additional_hours <= abs(configured_addition_hours * 60):
                    duration -= 1
        value.update({'duration': duration})
        return value


# 预定单
class HotelReservationLine(models.Model):
    _name = "hotel_reservation.line"
    _description = "Reservation Line"

    name = fields.Char('Name')
    # 预定单
    line_id = fields.Many2one('hotel.reservation')
    # 预约房间
    reserve = fields.Many2many('hotel.room',
                               'hotel_reservation_line_room_rel',
                               'hotel_reservation_line_id', 'room_id',
                               domain="[('isroom','=',True),('categ_id','=',categ_id)]")
    # 场地类型
    categ_id = fields.Many2one('hotel.room.type', 'Space Type')

    @api.onchange('categ_id')
    def on_change_categ(self):
        '''
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        '''
        hotel_room_obj = self.env['hotel.room']
        hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
                                                 self.categ_id.id)])
        room_ids = []
        if not self.line_id.checkin or not self.line_id.checkout:
            raise ValidationError(_('Before choosing a room,\n You have to \
                                     select a Check in date or a Check out \
                                     date in the reservation form.'))
        checkin = self.line_id.checkin
        checkout = self.line_id.checkout

        for room in hotel_room_ids:
            assigned = False

            # 遍历该场地的预约单
            for line in room.room_reservation_line_ids:
                # 如果状态为取消
                if line.status != 'cancel':
                    #
                    if (self.line_id.checkin <= line.check_in <= self.line_id.checkout) \
                            or (self.line_id.checkin <= line.check_out <= self.line_id.checkout):
                        assigned = True
                    elif (line.check_in <= self.line_id.checkin <=
                          line.check_out) or (line.check_in <=
                                              self.line_id.checkout <=
                                              line.check_out):
                        assigned = True
            # 遍历房间的账单
            for rm_line in room.room_line_ids:
                # 如果账单状态不是取消状态
                if rm_line.status != 'cancel':
                    if (self.line_id.checkin <= rm_line.check_in <= self.line_id.checkout) \
                            or (self.line_id.checkin <= rm_line.check_out <= self.line_id.checkout):
                        assigned = True
                    elif (rm_line.check_in <= self.line_id.checkin <=
                          rm_line.check_out) or (rm_line.check_in <=
                                                 self.line_id.checkout <=
                                                 rm_line.check_out):
                        assigned = True

            # 房间不开放判断
            for obj in room.room_reservation_period_ids:
                # 如果有重叠时间，则不显示
                if not (obj.start_date > checkout or checkin > obj.end_date):
                    assigned = True
                    break
            if not assigned:
                room_ids.append(room.id)
        domain = {'reserve': [('id', 'in', room_ids)]}
        return {'domain': domain}

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        hotel_room_reserv_line_obj = self.env['hotel.room.reservation.line']
        for reserv_rec in self:
            for rec in reserv_rec.reserve:
                hres_arg = [('room_id', '=', rec.id),
                            ('reservation_id', '=', reserv_rec.line_id.id)]
                myobj = hotel_room_reserv_line_obj.search(hres_arg)
                if myobj.ids:
                    rec.write({'isroom': True, 'status': 'available'})
                    myobj.unlink()
        return super(HotelReservationLine, self).unlink()


# 空间预定信息（针对空间）
class HotelRoomReservationLine(models.Model):
    _name = 'hotel.room.reservation.line'
    _description = 'Space Reservation'
    _rec_name = 'room_id'

    # 场地预定
    room_id = fields.Many2one('hotel.room', string='Space id')
    # 开始使用时间
    check_in = fields.Datetime('Start Time', required=True)
    # 结束使用时间
    check_out = fields.Datetime('End Time', required=True)
    # 状态：已分配，未分配
    state = fields.Selection([('assigned', 'Assigned'),
                              ('unassigned', 'Unassigned')], 'Space Status')
    # 预定单id
    reservation_id = fields.Many2one('hotel.reservation',
                                     string='Reservation')
    # 预定单状态
    status = fields.Selection(string='state', related='reservation_id.state')


# 继承空间添加预定列表
class HotelRoom(models.Model):
    _inherit = 'hotel.room'
    _description = 'Space'

    room_reservation_line_ids = fields.One2many('hotel.room.reservation.line',
                                                'room_id',
                                                string='Space Reserve Line')
    room_reservation_period_ids = fields.One2many(comodel_name='room.reservation.period', inverse_name='room_id',
                                                  string='Open appointment time')

    @api.multi
    def write(self, vals):
        # print(vals)
        return super(HotelRoom, self).write(vals)

    # @api.constrains('room_reservation_period_ids')
    # def _onchange_room_reservation_period_ids(self):
    #     for p_ids in self:
    #         for p in p_ids.room_reservation_period_ids:
    #             if not p.available:
    #                 continue
    #             if p.end_dete < p.start_date:
    #                 raise ValidationError(_('End Date cannot be greater than start Date'))

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        在预订的确认状态下，用户无法删除房间
        @param self: The object pointer
        @return: True/False.
        """
        for room in self:
            for reserv_line in room.room_reservation_line_ids:
                if reserv_line.status == 'confirm':
                    raise ValidationError(
                        _('User is not able to delete the room after the room in %s state  in reservation') % (
                            reserv_line.status))
        return super(HotelRoom, self).unlink()

    @api.model
    def cron_room_line(self):
        """
        This method is for scheduler
        every 1min scheduler will call this method and check Status of
        room is occupied or available
        此方法用于调度程序，每1分钟调度程序将调用此方法并检查房间的状态是否已被占用或可用
        --------------------------------------------------------------
        @param self: The object pointer
        @return: update status of hotel room reservation line
        """
        reservation_line_obj = self.env['hotel.room.reservation.line']
        folio_room_line_obj = self.env['folio.room.line']
        now = datetime.now()
        curr_date = now.strftime(dt)
        for room in self.search([]):
            reserv_line_ids = [reservation_line.id for
                               reservation_line in
                               room.room_reservation_line_ids]
            reserv_args = [('id', 'in', reserv_line_ids),
                           ('check_in', '<=', curr_date),
                           ('check_out', '>=', curr_date)]
            reservation_line_ids = reservation_line_obj.search(reserv_args)
            rooms_ids = [room_line.ids for room_line in room.room_line_ids]
            rom_args = [('id', 'in', rooms_ids),
                        ('check_in', '<=', curr_date),
                        ('check_out', '>=', curr_date)]
            room_line_ids = folio_room_line_obj.search(rom_args)
            status = {'isroom': True, 'color': 5}
            if reservation_line_ids.ids:
                status = {'isroom': False, 'color': 2}
            room.write(status)
            if room_line_ids.ids:
                status = {'isroom': False, 'color': 2}
            room.write(status)
            if reservation_line_ids.ids and room_line_ids.ids:
                raise ValidationError(_('Please Check Spaces Status \
                                         for %s.' % (room.name)))
        return True


# 空间申请摘要
class RoomReservationSummary(models.Model):
    _name = 'room.reservation.summary'
    _description = 'Space reservation summary'

    name = fields.Char('Reservation Summary', default='Reservations Summary',
                       invisible=True)
    # 日期开始
    date_from = fields.Datetime('Date From')
    # 至日期
    date_to = fields.Datetime('Date To')
    # 汇总表头
    summary_header = fields.Text('Summary Header')
    # 房间汇总
    room_summary = fields.Text('Space Summary')

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        获取对象的默认值
        @param self: The object pointer.
        @param fields: List of fields for which we want default values 我们想要默认值的字段列表
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(RoomReservationSummary, self).default_get(fields)
        # Added default datetime as today and date to as today + 30.
        from_dt = datetime.today()
        dt_from = from_dt.strftime(dt)
        to_dt = from_dt + relativedelta(days=30)
        dt_to = to_dt.strftime(dt)
        res.update({'date_from': dt_from, 'date_to': dt_to})

        if not self.date_from and self.date_to:
            date_today = datetime.datetime.today()
            first_day = datetime.datetime(date_today.year,
                                          date_today.month, 1, 0, 0, 0)
            first_temp_day = first_day + relativedelta(months=1)
            last_temp_day = first_temp_day - relativedelta(days=1)
            last_day = datetime.datetime(last_temp_day.year,
                                         last_temp_day.month,
                                         last_temp_day.day, 23, 59, 59)
            date_froms = first_day.strftime(dt)
            date_ends = last_day.strftime(dt)
            res.update({'date_from': date_froms, 'date_to': date_ends})
        return res

    @api.multi
    def room_reservation(self):
        '''
        @param self: object pointer
        '''
        mod_obj = self.env['ir.model.data']
        if self._context is None:
            self._context = {}
        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=',
                                          'view_hotel_reservation_form')])
        resource_id = model_data_ids.read(fields=['res_id'])[0]['res_id']
        return {'name': _('Reconcile Write-Off'),
                'context': self._context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hotel.reservation',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }

    @api.onchange('date_from', 'date_to')
    def get_room_summary(self):
        '''
        @param self: object pointer
         '''
        res = {}
        all_detail = []
        room_obj = self.env['hotel.room']
        reservation_line_obj = self.env['hotel.room.reservation.line']
        folio_room_line_obj = self.env['folio.room.line']
        user_obj = self.env['res.users']
        date_range_list = []
        main_header = []
        summary_header_list = ['Rooms']
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_('Please Check Time period Date From can\'t \
                                   be greater than Date To !'))
            if self._context.get('tz', False):
                timezone = pytz.timezone(self._context.get('tz', False))
            else:
                timezone = pytz.timezone('UTC')
            d_frm_obj = (self.date_from).replace(tzinfo=pytz.timezone('UTC')
                                                 ).astimezone(timezone)
            d_to_obj = (self.date_to).replace(tzinfo=pytz.timezone('UTC')
                                              ).astimezone(timezone)
            temp_date = d_frm_obj
            while (temp_date <= d_to_obj):
                val = ''
                val = (str(temp_date.strftime("%a")) + ' ' +
                       str(temp_date.strftime("%b")) + ' ' +
                       str(temp_date.strftime("%d")))
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime(dt))
                temp_date = temp_date + timedelta(days=1)
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([])
            all_room_detail = []
            for room in room_ids:
                room_detail = {}
                room_list_stats = []
                room_detail.update({'name': room.name or ''})
                if not room.room_reservation_line_ids and \
                        not room.room_line_ids:
                    for chk_date in date_range_list:
                        room_list_stats.append({'state': 'Free',
                                                'date': chk_date,
                                                'room_id': room.id})
                else:
                    for chk_date in date_range_list:
                        ch_dt = chk_date[:10] + ' 23:59:59'
                        ttime = datetime.strptime(ch_dt, dt)
                        c = ttime.replace(tzinfo=timezone). \
                            astimezone(pytz.timezone('UTC'))
                        chk_date = c.strftime(dt)
                        reserline_ids = room.room_reservation_line_ids.ids
                        reservline_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>=', chk_date),
                                            ('state', '=', 'assigned')
                                            ]))
                        if not reservline_ids:
                            sdt = dt
                            chk_date = datetime.strptime(chk_date, sdt)
                            chk_date = datetime. \
                                strftime(chk_date - timedelta(days=1), sdt)
                            reservline_ids = (reservation_line_obj.search
                                              ([('id', 'in', reserline_ids),
                                                ('check_in', '<=', chk_date),
                                                ('check_out', '>=', chk_date),
                                                ('state', '=', 'assigned')]))
                            for res_room in reservline_ids:
                                cid = res_room.check_in
                                cod = res_room.check_out
                                dur = cod - cid
                                if room_list_stats:
                                    count = 0
                                    for rlist in room_list_stats:
                                        cidst = datetime.strftime(cid, dt)
                                        codst = datetime.strftime(cod, dt)
                                        rm_id = res_room.room_id.id
                                        ci = rlist.get('date') >= cidst
                                        co = rlist.get('date') <= codst
                                        rm = rlist.get('room_id') == rm_id
                                        st = rlist.get('state') == 'Reserved'
                                        if ci and co and rm and st:
                                            count += 1
                                    if count - dur.days == 0:
                                        c_id1 = user_obj.browse(self._uid)
                                        c_id = c_id1.company_id
                                        con_add = 0
                                        amin = 0.0
                                        if c_id:
                                            con_add = c_id.additional_hours
                                        #                                        When configured_addition_hours is
                                        #                                        greater than zero then we calculate
                                        #                                        additional minutes
                                        if con_add > 0:
                                            amin = abs(con_add * 60)
                                        hr_dur = abs((dur.seconds / 60))
                                        #                                        When additional minutes is greater
                                        #                                        than zero then check duration with
                                        #                                        extra minutes and give the room
                                        #                                        reservation status is reserved or
                                        #                                        free
                                        if amin > 0:
                                            if hr_dur >= amin:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                        else:
                                            if hr_dur > 0:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                    else:
                                        reservline_ids = False
                        fol_room_line_ids = room.room_line_ids.ids
                        chk_state = ['draft', 'cancel']
                        folio_resrv_ids = (folio_room_line_obj.search
                                           ([('id', 'in', fol_room_line_ids),
                                             ('check_in', '<=', chk_date),
                                             ('check_out', '>=', chk_date),
                                             ('status', 'not in', chk_state)
                                             ]))
                        # 如果预约了或者已经生成账单
                        # print(folio_resrv_ids)
                        # if reservline_ids or folio_resrv_ids:
                        if reservline_ids:
                            room_list_stats.append({'state': 'Reserved',
                                                    'date': chk_date,
                                                    'room_id': room.id,
                                                    'is_draft': 'No',
                                                    'data_model': '',
                                                    'data_id': 0})
                        else:
                            room_list_stats.append({'state': 'Free',
                                                    'date': chk_date,
                                                    'room_id': room.id})

                room_detail.update({'value': room_list_stats})
                all_room_detail.append(room_detail)
            main_header.append({'header': summary_header_list})
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)
        return res


class QuickRoomReservation(models.TransientModel):
    _name = 'quick.room.reservation'
    _description = 'Quick Space Reservation'

    partner_id = fields.Many2one('res.partner', string="Customer",
                                 required=True)
    check_in = fields.Datetime('Start Time', required=True)
    check_out = fields.Datetime('End Time', required=True)
    room_id = fields.Many2one('hotel.room', 'Space', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Space Provider', required=True)
    pricelist_id = fields.Many2one('product.pricelist', 'pricelist')
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address',
                                         required=True)
    partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
                                       required=True)
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address',
                                          required=True)
    adults = fields.Integer('Adults', size=64)

    @api.onchange('check_out', 'check_in')
    def on_change_check_out(self):
        '''
        When you change checkout or checkin it will check whether
        Checkout date should be greater than Checkin date
        and update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        '''
        if self.check_out and self.check_in:
            if self.check_out < self.check_in:
                raise ValidationError(_('Checkout date should be greater \
                                         than Checkin date.'))

    @api.onchange('partner_id')
    def onchange_partner_id_res(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        '''
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
            self.partner_order_id = False
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice',
                                                'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(QuickRoomReservation, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                res.update({'check_in': self._context['date']})
            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
        return res

    @api.multi
    def room_reserve(self):
        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        hotel_res_obj = self.env['hotel.reservation']
        for res in self:
            rec = (hotel_res_obj.create
                   ({'partner_id': res.partner_id.id,
                     'partner_invoice_id': res.partner_invoice_id.id,
                     'partner_order_id': res.partner_order_id.id,
                     'partner_shipping_id': res.partner_shipping_id.id,
                     'checkin': res.check_in,
                     'checkout': res.check_out,
                     'warehouse_id': res.warehouse_id.id,
                     'pricelist_id': res.pricelist_id.id,
                     'adults': res.adults,
                     'reservation_line': [(0, 0,
                                           {'reserve': [(6, 0,
                                                         [res.room_id.id])],
                                            'name': (res.room_id and
                                                     res.room_id.name or '')
                                            })]
                     }))
        return rec


# -------------- Add ------------------
class RoomReservationPeriod(models.Model):
    _name = 'room.reservation.period'
    _description = 'Space Open appointment time'

    room_id = fields.Many2one('hotel.room', string='Space id')
    # start_hour = fields.Integer(string='Start Hour')
    # end_hour = fields.Integer(string='End Hour')
    start_date = fields.Datetime(string='Start Time', required=True, )
    end_date = fields.Datetime(string='End Time', required=True, )
    available = fields.Boolean(string='Available', default=True)

    @api.constrains('start_date', 'end_date')
    def check_hour(self):
        for obj in self:
            if obj.start_date and obj.end_date:
                if obj.start_date > obj.end_date:
                    raise ValidationError(_('End DateTime date should be greater \
                                             than Start DateTime.'))
