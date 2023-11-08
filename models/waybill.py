from odoo import models, fields, api
from odoo import tools
from datetime import datetime, timedelta
import pytz


class Waybill(models.Model):
    _name = 'waybill'
    _description = 'Waybill'

    # 生成自定义编号数据
    def generate_custom_code(self):
        # 获取当前用户时区
        tz_name = self._context.get('tz') or self.env.user.tz
        # 计算当前时区和UTC0时差       
        utc_time = fields.Datetime.now()
        local_time = utc_time.astimezone(pytz.timezone(tz_name))
        date_format = "%Y-%m-%d %H:%M:%S"
        string_utc = utc_time.strftime(date_format)
        string_local = local_time.strftime(date_format)
        datetime_utc = datetime.strptime(string_utc, date_format)
        datetime_local = datetime.strptime(string_local, date_format)
        time_difference = (datetime_local-datetime_utc).total_seconds()/3600
        tz_hours = timedelta(hours=time_difference)
        hours = timedelta(hours=24-time_difference)
        # 构造查询数据条件
        current_time = fields.Datetime.now()
        local_date = (current_time + tz_hours).replace(hour=0,
                                                       minute=0, second=0, microsecond=0)
        date_start = local_date-tz_hours
        date_end = local_date+hours
        record_count = self.search_count(
            [('create_date', '>=', date_start), ('create_date', '<', date_end)])
        return f'HY{local_date.strftime("%Y%m%d")}{record_count + 1:04d}'

    goods_num_auto = fields.Char(
        string='货运单编号', default=generate_custom_code, readonly=True)
    goods_num = fields.Char(string='自编号')
    destination = fields.Many2one('city', string='目的站', required=True)
    receiver_id = fields.Many2one('receiver', string='收货人', required=True)
    receiver_tel = fields.Char(
        string="收货人电话", store=False, readonly=True, compute="_compute_customerInfo")
    receiver_address = fields.Char(
        string="收货人地址", store=False, readonly=True, compute="_compute_customerInfo")
    shipper_id = fields.Many2one('shipper', string='发货人', required=True)
    shipper_tel = fields.Char(
        string="发货人电话", store=False, readonly=True, compute="_compute_customerInfo")

    servicetype = fields.Selection(
        [('1', '站到站'),
         ('2', '中转'),
         ('3', '外包'), ],
        string='服务方式', default="1")
    paytype = fields.Selection(
        [('1', '现付'),
         ('2', '到付'),
         ('3', '月结'), ],
        string='付款方式', default="1")

    total_fees = fields.Float(string='总运费', compute='_compute_total_fees', store=True)
    receiving_fees = fields.Float(string='接货费')
    deliver_fees = fields.Float(string='送货费')
    substitute_fees = fields.Float(string='垫付费')
    transfer_fees = fields.Float(string='中转费')
    load_unload_fees = fields.Float(string='装卸费')
    guarantee_fees = fields.Float(string='保管费')

    collect_fees = fields.Char(string='代收款')

    refund = fields.Char(string='返款')
    # current_location = fields.Char(string='到达地', required=True)
    # amount_receivable = fields.Char(string='应收余额', required=True)
    # examine = fields.Char(string='审核', required=True)
    status = fields.Selection(
        [('1', '待收货'),
         ('2', '待装运'),
         ('3', '待发货'),
         ('4', '运输中'),
         ('5', '已到达'),
         ('6', '已签收')],
        string='运单状态', default="3")
    # 复制数据的时候，创建时间和修改时间不复制
    create_date = fields.Datetime(string='创建时间', readonly=True, copy=False)
    write_date = fields.Datetime(string='修改时间', readonly=True, copy=False)

    detail_ids = fields.One2many('waybill.detail', 'waybill_id', string='货运明细')

    # 确保在复制的时候自定义编号数据生效
    def copy(self, default=None):
        if default is None:
            default = {}
        default['goods_num_auto'] = self.generate_custom_code()
        return super(Waybill, self).copy(default)

    @api.onchange('receiver_id')
    def _onchange_receiver_id(self):
        if self.receiver_id:
            self.receiver_tel = self.receiver_id.tel
            self.receiver_address = self.receiver_id.address

    @api.onchange('shipper_id')
    def _onchange_shipper_id(self):
        if self.shipper_id:
            self.shipper_tel = self.shipper_id.tel

    @api.depends('shipper_id', 'receiver_id')
    def _compute_customerInfo(self):
        for customer in self:
            customer.receiver_tel = customer.receiver_id.tel
            customer.receiver_address = customer.receiver_id.address
            customer.shipper_tel = customer.shipper_id.tel

    # 重载name_get()方法
    def name_get(self):
        result = []
        for record in self:
            # rec_name = "%s[%s %s %s]" % (record.goods_num_auto, record.destination.city_name,record.receiver_id.receiver_name, record.receiver_id.tel)
            rec_name = "%s" % (record.goods_num_auto)
            result.append((record.id, rec_name))
        return result
    
    @api.depends('detail_ids.total_freight')
    def _compute_total_fees(self):
        for waybill in self:
            waybill.total_fees = sum(waybill.detail_ids.mapped('total_freight'))


class WaybillDetail(models.Model):
    _name = 'waybill.detail'
    _description = 'Waybill Detail'

    goods_id = fields.Many2one('goods', string='货物名称', required=True)
    package_id = fields.Many2one('package', string='包装', required=True)
    unit_price = fields.Char(string='单价', default=0)
    quantity = fields.Char(string='数量', default=1)
    weight = fields.Float(string='重量')
    volume = fields.Float(string='体积')
    pricing_mode = fields.Selection(
        [('1', '按单价'),
         ('2', '按重量'),
         ('3', '按体积')],
        string='计价方式', default="1")
    rates = fields.Many2one('rate', string='费率')
    total_freight = fields.Float(string='运费合计')

    waybill_id = fields.Many2one('waybill', string='货运表')

    @api.onchange('pricing_mode', 'volume', 'weight', 'quantity', 'unit_price', 'rates')
    def _onchange_to_total_freight(self):
        match self.pricing_mode:
            case "1":
                self.total_freight = self.unit_price
            case "2":
                self.total_freight = self.weight*self.rates.rate_value
            case "3":
                self.total_freight = self.volume*self.rates.rate_value
