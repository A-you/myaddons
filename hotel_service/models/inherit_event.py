# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/9/3 16:37
"""
from odoo import models,fields,api

class InhertEventEvent(models.Model):
	_inherit = 'event.event'

	service_product_id = fields.Many2one('hotel.services',string='关联服务')
	service_description = fields.Html(string='描述')
	service_image = fields.Binary(string='图片',attachment=True)
	image_url = fields.Char(string='图片地址',compute='_compute_display_url')

	start_hour = fields.Float('起', default=7,help='一天中,活动开展的时间起')
	end_hour = fields.Float('止', default=23,help='一天中,活动开展的时间止')

	event_addr = fields.Char(string='地址')

	def _get_attachments(self, attachments):
		return ', '.join([k.name for k in attachments])

	@api.depends('service_image')
	def _compute_display_url(self):
		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		for line in self:
			line.image_url = '%s/web/image?model=event.event&id=%s&field=service_image' % (base_url, line.id)

	# def get_main_image(self):
	# 	base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
	# 	# print base_url
	# 	return '%s/web/image/event.event/%s/image/80x80' % (base_url, self.id)
