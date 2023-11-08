from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Package(models.Model):
    _name = 'package'
    _description = 'Package'
    _rec_name = "package_name"

    package_name = fields.Char(string='货物名称', required=True)


    @api.constrains('package_name')
    def _check_unique_package_name(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('package_name', '=', record.package_name)]) > 1:
                raise ValidationError("包装名称重复")