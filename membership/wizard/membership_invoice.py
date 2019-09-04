# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MembershipInvoice(models.TransientModel):
    _name = "membership.invoice"
    _description = "Membership Invoice"

    product_id = fields.Many2one('product.product', string='Membership', required=True)
    pricelist_id = fields.Many2one('product.pricelist.item',string='Price List')
    member_price = fields.Float(string='Member Price', digits=dp.get_precision('Product Price'), required=True)
    # member_price = fields.Float(string='Member Price', required=True)
    @api.onchange('product_id')
    def onchange_product(self):
        """This function returns value of  product's member price based on product id.
        """
        price_dict = self.product_id.price_compute('list_price')
        for x in self.product_id.membership_service_type_ids:
	        print(x.hotel_service_type_id.name, x.percentage_ids.name)
        # print(self.product_id.membership_service_type_ids)
        self.member_price = price_dict.get(self.product_id.id) or False
        # print(self.product_id.item_ids)
        domain_ids = []
        for x in self.product_id.item_ids:
            domain_ids.append(x.id)
        return {
            'domain': {'pricelist_id': [('id','in',domain_ids)]}
        }



    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
		# self.member_price = float(self.pricelist_id.fixed_price)
        pass


    @api.multi
    def membership_invoice(self):
        datas={}
        print(self.member_price)
        if self:
            datas = {
                'membership_product_id': self.product_id.id,
                'amount': self.member_price
            }
        # 创建会员发票
        # invoice_list = self.env['res.partner'].browse(self._context.get('active_ids')).create_membership_invoice(
        #     datas=datas)
        self.env['res.partner'].browse(self._context.get('active_ids')).create_membership_invoice(datas=datas)


        return True
