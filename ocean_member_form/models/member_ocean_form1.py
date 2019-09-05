# encoding: utf-8

"""
@author: you
@site: 
@time: 2019/7/22 11:14
"""

from odoo import  fields,models,api

class MemberOceanMagazeum(models.Model):
	_name = 'ocean.member.form1'
	_description = '博志会员申请表'
	_rec_name = 'partner_id'

	#品牌网站
	brand_website = fields.Char(string='BrandWebsite')

	#品牌来源
	brand_origin = fields.Many2one('res.country',string='品牌来源')
	# brand_origin = fields.Char(string='品牌来源')

	#经营模式
	# nature_business = fields.Many2one('member.ocean.maga.nature',string='经营模式')
	nature_business = fields.Many2one('ocean.member.nature.business',string='经营模式')
	# nature_business = fields.Char(string='经营模式')

	#产品分类
	product_category_ids = fields.Many2many('ocean.form.product.category', string='产品分类')

	#目标客群
	gender = fields.Selection([(1,'男'),(0,'女')],default=1,string='性别')
	age_group = fields.Selection([(1,'18岁以下'),(2,'19-29岁'),(3,'30-39岁'),(4,'40-49'),(5,'50岁以上')],default=2,string='年龄分组')
	education = fields.Selection([(1,'高中'),(2,'大学'),(3,'无要求')],default=1,string='学历水平')
	occupation = fields.Char(string='职业')
	income = fields.Char(string='收入水平')
	interest = fields.Char(string='兴趣爱好')
	other_costumer_attr = fields.Text(string='其他')


	#在中国竞争对手
	china_opponents = fields.Many2many('ocean.member.opponent',string='在中国')
	#在来源国竞争对手
	source_opponents = fields.Many2many('ocean.member.opponent',string='来源国')

	#意向需求
	service_needed_ids = fields.Many2many('ocean.form.service.line',string='需求意向')

	#联络人
	partner_id = fields.Many2one('res.partner',string='联络人')

	#品牌描述
	brand_description= fields.Text(string='品牌描述')

	attachment_number = fields.Integer(compute='_compute_attachment_number', string='附件上传')

	@api.multi
	def _compute_attachment_number(self):
		"""附件上传"""
		attachment_data = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'ocean.member.form1'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
		attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
		for expense in self:
			expense.attachment_number = attachment.get(expense.id, 0)

	@api.multi
	def action_get_attachment_view(self):
		"""附件上传动作视图"""
		self.ensure_one()
		res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
		res['domain'] = [('res_model', '=', 'ocean.member.form1'), ('res_id', 'in', self.ids)]
		res['context'] = {'default_res_model': 'ocean.member.form1', 'default_res_id': self.id}
		return res




