from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Goods(models.Model):
    _name = 'goods'
    _description = 'Goods'
    _rec_name = "goods_name"

    goods_name = fields.Char(string='Goods Name', required=True)


    @api.constrains('goods_name')
    def _check_unique_goods_name(self):
        for record in self:
            # 检查是否有其他记录具有相同的名称
            if self.search_count([('goods_name', '=', record.goods_name)]) > 1:
                raise ValidationError("Duplicate goods name")