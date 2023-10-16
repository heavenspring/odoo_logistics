from odoo import models, fields,api

class Waybill(models.Model):
    _name = 'waybill'
    _description = 'waybill'

    goods_num_auto = fields.Char(string='货运单编号', required=True)
    goods_num = fields.Char(string='自编号', required=True)
    destination = fields.Char(string='目的站', required=True)
    receiver = fields.Char(string='收货人', required=True)
    tel = fields.Char(string='电话', required=True)
    mobile = fields.Char(string='手机', required=True)
    goods_name = fields.Char(string='货物名称', required=True)
    package = fields.Char(string='包装', required=True)
    unit_price = fields.Char(string='单价', required=True)
    quantity = fields.Char(string='数量', required=True)
    weight = fields.Char(string='重量', required=True)
    volume = fields.Char(string='体积', required=True)
    pricing_mode = fields.Char(string='计价方式', required=True)
    total_freight = fields.Char(string='运费合计', required=True)
    paytype = fields.Char(string='付款方式', required=True)
    collect_fees = fields.Char(string='代收款', required=True)
    substitute_payment = fields.Char(string='垫付款', required=True)
    refund = fields.Char(string='返款', required=True)
    current_location = fields.Char(string='到达地', required=True)
    amount_receivable = fields.Char(string='应收余额', required=True)
    examine = fields.Char(string='审核', required=True)
    status = fields.Char(string='运单状态', required=True)