# -*- coding: utf-8 -*-
from odoo import models, api, fields


class Users(models.Model):
    _inherit = 'res.users'
    fields.Binary
    job_name = fields.Char(u'岗位', compute='_compute_job_name')

    def _compute_job_name(self):
        employee_obj = self.env['hr.employee'].sudo()
        for user in self:
            employee = employee_obj.search([('user_id', '=', user.id)], limit=1)
            if employee and employee.job_id:
                user.job_name = employee.job_id.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # 一个节点有多个用户符合审批条件，需指定其中一个人来审批该节点，user_id_domain的值来限制该节点可以由哪些用户来审批
        context = self._context or {}

        if 'node_type' in context:
            node_type = context['node_type']
            if node_type == 'free':
                if 'groups_id' in context:
                    print(context['groups_id'])
                    groups_id = context['groups_id']
                    users_obj = self.env['res.users'].sudo()
                    users = users_obj.search([('share', '=', False)])
                    exist_users = users.filtered(lambda user: groups_id in user.groups_id.ids)
                    current_user_id = self.env.user.id
                    user_id_domain = exist_users.ids
                    if current_user_id in user_id_domain:
                        user_id_domain.remove(current_user_id)
                    args = args or []
                    args.append(('id', 'in', user_id_domain))
            else:
                if 'user_id_domain' in context:
                    if context['user_id_domain']:
                        user_id_domain = [int(user_id) for user_id in context['user_id_domain'].split(',')]

                        # 不含当前登陆用户
                        current_user_id = self.env.user.id
                        if current_user_id in user_id_domain:
                            user_id_domain.remove(current_user_id)

                        args = args or []
                        args.append(('id', 'in', user_id_domain))

        return super(Users, self).name_search(name, args=args, operator=operator, limit=limit)


class Groups(models.Model):
    _inherit = "res.groups"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        context = self._context or {}
        if 'node_type' in context:
            node_type = context['node_type']
            print(node_type)
            if node_type == 'free':
                if 'groups_id_domain' in context:
                    print(context['groups_id_domain'])
                    groups_id_domain = [int(groups_id) for groups_id in context['groups_id_domain'].split(',')]

                    args = args or []
                    args.append(('id', 'in', groups_id_domain))

        return super(Groups, self).name_search(name, args=args, operator=operator, limit=limit)
