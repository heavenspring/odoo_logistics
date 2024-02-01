from odoo import models, fields,api
from odoo.exceptions import ValidationError

class City(models.Model):
    _name = 'city'
    _description = 'City'
    _rec_name = "city_name"

    city_name = fields.Char(string='City Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, domain="[('is_company', '=', True)]")


    def name_get(self):  # 重写name_get()方法
        result = []

        for record in self:
            rec_name = "%s[%s]" % (record.city_name, record.partner_id.name)
            result.append((record.id, rec_name))
            # if record.context_info:
            #     rec_name = "%s[%s]" % (record.city_name, record.partner_id.name)
            #     result.append((record.id, rec_name))
            # else:
            #     result.append(super(City, record).name_get()[0])       
        return result

    @api.constrains('city_name')
    def _check_unique_city_name(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('city_name', '=', record.city_name),('partner_id', '=', record.partner_id.id)]) > 1:
                raise ValidationError("Duplicate data")