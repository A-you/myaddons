from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class MembershipConsumptionDetailsWizard(models.TransientModel):
    _name = 'membership_statement.wizard'
    partner = fields.Many2one('res.partner', 'Member', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date',  required=True)

    # 调用打印
    @api.multi
    def report_membership_statement(self):
        data = {
            'ids': self.ids,
            'model': 'membership.membership_line',
            'form': {'id': self.id, 'start_date': self.start_date, 'end_date': self.end_date, 'partner': [self.partner.id, self.partner.name]}
        }
        return self.env.ref('membership_statement.report_membership_consumption_details_management'
                            ).report_action(self, data=data)
    # 判断前后时间
    @api.onchange('end_date', 'start_date')
    def _judgment_of_time(self):
        for i in self:
            if i.end_date:
                start_date = i.start_date
                end_date = i.end_date
                if start_date:
                    if (end_date - start_date).days < 0:
                        raise ValidationError("The end time must be greater than the start time.")




