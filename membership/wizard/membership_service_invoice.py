from odoo import api, models, fields,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
USE_POINTS = [
    ('person', 'Person'),
    ('company', 'Company'),
]

DOMAIN_IDS = []

class MembershipServicesInvoice(models.TransientModel):
    _name = 'membership.services.invoice'
    _description = 'Membership Services Invoice'
    # domain_ids = []
    product_ids = fields.Many2one(comodel_name='hotel.services', string='Membership Service', required=True)
    is_use_company = fields.Boolean('Use Company Points')
    total_price = fields.Float(string='Total Points', digits=dp.get_precision('Product Price'))
    
    @api.multi
    @api.onchange('product_ids')
    def onchange_product(self):
        """
        根据选择
        """
        self.total_price = self.product_ids.product_id.product_tmpl_id.list_price
        domain_ids = []
        seller_ids = self.env['product.supplierinfo'].sudo().search([('product_tmpl_id', '=', self.product_ids.product_id.product_tmpl_id.id)])
        for seller_id in seller_ids:
            domain_ids.append(seller_id.id)
        if domain_ids:
            return {
                'domain': {'seller_id':[('id','in',domain_ids)]}
            }
        return {
                'domain': {'seller_id':[]}
            }

    seller_id = fields.Many2one('product.supplierinfo',string='供应商' )

    @api.onchange('seller_id')
    def onchange_seller(self):
        seller_id = self.env['product.supplierinfo'].sudo().search(
            [('product_tmpl_id', '=', self.product_ids.product_id.product_tmpl_id.id),('id','=',self.seller_id.id)])
        if seller_id.price:
            self.total_price = seller_id.price


    @api.multi
    def service_invoice(self):
        state = "paid"
        for x in self:
            if x.product_ids[0].auto_approval:
                state = "audit"
            _dict = {
                "partner_id": x._context.get('active_ids')[0],
                "membership_server": x.product_ids[0].id,
                "state": state,
                # "service_price": x.product_ids[0].product_id.product_tmpl_id.list_price,
                "service_price": x.total_price,
                'seller_id': x.seller_id.id
            }
            try:
                x.env['membership.service_line'].sudo().create(_dict)
                return True
            except Exception as e:
                raise ValidationError(_(e))



