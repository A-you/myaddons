#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/9/18 18:02
# @Author : Ymy
from odoo import api, fields, models, _

class ServiceFormConfigure(models.Model):
	_name = 'service.form.configure'
	_description = u'会员预约表单配置，前端vue组件化配置'

	name = fields.Char(string='名称')