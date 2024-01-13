from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Driver(models.Model):
    _name = 'driver'
    _description = 'Driver'
    _rec_name = "driver_name"

    driver_name = fields.Char(string='Driver Name', required=True)
    plate_number = fields.Char(string='Plate Number', required=True)

    # 重写name_get()方法
    def name_get(self): 
        result = []
        for record in self:
            rec_name = "%s[%s]" % (record.driver_name, record.plate_number)
            result.append((record.id, rec_name))
        return result

    @api.constrains('driver_name')
    def _check_unique_goods_name(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('driver_name', '=', record.driver_name),('plate_number', '=', record.plate_number)]) > 1:
                raise ValidationError("Duplicate data")