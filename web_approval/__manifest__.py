# -*- coding: utf-8 -*-
{
    'name': 'Web Approval',
    'category': 'Approval',
    'author': 'Lecoo',
    'version': '12.2.0',
    'summary': '审批流程',
    'description': """
    实现条件审批、会签、代签、沟通、抄送功能
    luhuan97@foxmail.com 二次修改
    原作者：675938238@qq.com
    """,
    'depends': ['web', 'mail', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/approval_flow_view.xml',
        'views/wait_approval_summary_view.xml',
        'views/record_approval_state_summary_view.xml',
        'views/approval_copy_for_summary_view.xml',
        'views/record_approval_state_view.xml',

        'views/assets.xml',

        'wizard/approval_wizard_view.xml',
        'wizard/dispatch_approval_user_wizard_veiw.xml',
        'wizard/approval_turn_to_wizard_view.xml',
        'wizard/add_node_action_wizard_view.xml',
        'wizard/approval_increase_wizard_view.xml',

        'data/approval_node.xml',
        'data/mail_message_subtype.xml',
        'data/mail_channel.xml',
        'data/increase_type.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'auto_install': False,
    'application': True
}
