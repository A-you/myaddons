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

	event_addr = fields.Char(string='活动地址')

	# _default_event_ticket_ids = [
	# 	(4,self.env)
	# ]

	#这不是一个好方案，放弃
	# def _default_event_ticket_ids(self):
	# 	return [
	# 		(4,self.env.ref('membership.membership_event_data_full_member').id)
	# 	]
	#
	# event_ticket_ids = fields.One2many(
	# 	'event.event.ticket', 'event_id', string='Event Ticket',
	# 	copy=True,default=_default_event_ticket_ids)

	def _get_attachments(self, attachments):
		return ', '.join([k.name for k in attachments])

	@api.depends('service_image')
	def _compute_display_url(self):
		for x in self:
			if x.service_image:
				base_url = x.env['ir.config_parameter'].sudo().get_param('web.base.url')
				for line in x:
					line.image_url = '%s/web/image?model=event.event&id=%s&field=service_image' % (base_url, line.id)

	# def get_main_image(self):
	# 	base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
	# 	# print base_url
	# 	return '%s/web/image/event.event/%s/image/80x80' % (base_url, self.id)


class EventTicket(models.Model):
	_inherit = 'event.event.ticket'

	membership_level = fields.Selection([(1,'非会员'),(2,'会员')], string='Level', default=1)