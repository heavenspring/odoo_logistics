from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Rate(models.Model):
    _name = 'rate'
    _description = 'Rate'
    _rec_name = "rate_value"

    rate_value=fields.Float(string="Rate",default=0)


    @api.constrains('rate_value')
    def _check_unique_rate_value(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('rate_value', '=', record.rate_value)]) > 1:
                raise ValidationError("Rate duplication")

