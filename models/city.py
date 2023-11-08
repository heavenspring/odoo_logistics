from odoo import models, fields,api
from odoo.exceptions import ValidationError

class City(models.Model):
    _name = 'city'
    _description = 'City'
    _rec_name = "city_name"

    city_name = fields.Char(string='城市名称', required=True)


    @api.constrains('city_name')
    def _check_unique_city_name(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('city_name', '=', record.city_name)]) > 1:
                raise ValidationError("城市名称重复")