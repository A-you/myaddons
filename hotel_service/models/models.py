# 作者：Lecoo
# 联系：luhuan97@foxmail.com

from odoo import models, fields, api

# 服务类型
from odoo.osv import expression

class ProductHotelServiceLine(models.Model):

    _name = "product.hotel.service.line"
    _rec_name = 'hotel_service_type_id'
    _description = 'Product Template Attribute Line'
    _order = 'id'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade', required=True, index=True)
    # hotel_service_type_id = fields.Many2one('hotel.service.type', string='ServiceType', ondelete='restrict', required=True, index=True)
    hotel_service_type_id = fields.Many2one('hotel.service.type', string='服务类型', ondelete='restrict', required=True, index=True)
    # percentage_ids = fields.Many2many('hotel.service.type.percentage', string='ServiceType Percentage')
    percentage_ids = fields.Many2many('hotel.service.type.percentage', string='百分比')

class HotelServiceTypePercentage(models.Model):
    _name = 'hotel.service.type.percentage'
    name = fields.Char(string='百分比')
    service_type_id = fields.Many2one('hotel.service.type',string='服务类型')

class HotelServiceType(models.Model):
    _name = "hotel.service.type"
    _description = "Service Type"

    name = fields.Char('Service Name', size=64, required=True)
    service_id = fields.Many2one('hotel.service.type', 'Service Category')
    child_ids = fields.One2many('hotel.service.type', 'service_id',
                                'Child Categories')

    #描述
    synopsis = fields.Text(string='简介')

    percentage_ids = fields.One2many('hotel.service.type.percentage', 'service_type_id', 'Values', copy=True)

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.service_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.service_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args,
                                             operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('service_id', 'in',
                                              categories.ids)], domain])
                else:
                    domain = expression.AND([[('service_id', 'in',
                                               category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator,
                                ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]),
                                     limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('membership_service', 'Membership Service')])
    # categ_id = fields.Many2one('hotel.service.type', string='Service Category',
    #                            required=True)
    # product_manager = fields.Many2one('res.users', string='Product Manager')


# class ProductProduct(models.Model):
#     _inherit = 'product.product'

# type = fields.Selection(selection_add=[('membership_service', 'Membership Service')])
# type = fields.Selection([('membership_service', 'Membership Service')], 'Type')


#     categ_id = fields.Many2one('hotel.service.type', string='Service Category', required=True)
#     product_manager = fields.Many2one('res.users', string='Product Manager')




# 服务
class HotelServices(models.Model):
    _name = 'hotel.services'

    product_id = fields.Many2one('product.product', 'Service_id',
                                 required=True, ondelete='cascade',
                                 delegate=True)
    categ_id = fields.Many2one('hotel.service.type', string='Service Category')
    product_manager = fields.Many2one('res.users', string='Product Manager')
    auto_approval = fields.Boolean(string='Need approval')
    # x_parent = fields.Many2one('hotel.services', 'Higher Level')
    x_parent = fields.Many2one('hotel.services', '上级')

    service_numbered = fields.Char(string='服务编号',readonly=True)

    even_ids = fields.One2many('event.event','service_product_id',string='活动条目')

    @api.multi
    def write(self, vals):
        # 生成会员编号
        if not self.service_numbered:
            vals['service_numbered'] = self.env['ir.sequence'].next_by_code(
                'hotel.services') or ''
        return super(HotelServices, self).write(vals)