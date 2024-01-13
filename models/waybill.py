from odoo import models, fields, api
from odoo import tools
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import ValidationError


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
        string='Waybill Number', default=generate_custom_code, readonly=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    goods_num = fields.Char(string='Self Numbering')
    destination = fields.Many2one('city', string='Destination', required=True)
    receiver_id = fields.Many2one('receiver', string='Consignee', required=True)
    receiver_tel = fields.Char(
        string="Consignee Phone", store=False, readonly=True, compute="_compute_customerInfo")
    receiver_address = fields.Char(
        string="Consignee Address", store=False, readonly=True, compute="_compute_customerInfo")
    shipper_id = fields.Many2one('shipper', string='Shipper', required=True)
    shipper_tel = fields.Char(
        string="Shipper Phone", store=False, readonly=True, compute="_compute_customerInfo")

    servicetype = fields.Selection(
        [('1', 'Station To Station'),
         ('2', 'Transfer'),
         ('3', 'Outsource'), ],
        string='Service Type', default="1")
    paytype = fields.Selection(
        [('1', 'Pay As You Go'),
         ('2', 'Payment Upon Arrival'),
         ('3', 'Monthly Settlement'), ],
        string='Payment Type', default="1")

    total_fees = fields.Float(string='Total Freight', compute='_compute_total_fees', store=True)
    receiving_fees = fields.Float(string='Pickup Fee')
    deliver_fees = fields.Float(string='Delivery Charges')
    substitute_fees = fields.Float(string='Advance Payment Fee')
    transfer_fees = fields.Float(string='Transfer Fee')
    load_unload_fees = fields.Float(string='Handling Cost')
    guarantee_fees = fields.Float(string='Storage Fee')

    collect_fees = fields.Char(string='Agency Fund')

    refund = fields.Char(string='Refund')

    status = fields.Selection(
        [('1', 'To Be Received'),
         ('2', 'To Be Shipped'),
         ('3', 'To Be Sent'),
         ('4', 'In Transit'),
         ('5', 'Arrived'),
         ('6', 'Have Been Signed')],
        string='Waybill Status', default="3")
    create_date = fields.Datetime(string='Created on', readonly=True, copy=False)
    write_date = fields.Datetime(string='Last Updated on', readonly=True, copy=False)

    detail_ids = fields.One2many('waybill.detail', 'waybill_id', string='Waybill Details')

    state = fields.Selection([('1','Draft'),
                              ('2','Confirmed'),
                              ('3','Settled')], default='1', string="Status")
    

    def action_confirm(self):
        self.state='2'

        
    def action_cancel(self):
        self.state = '1'


    def unlink(self):
        for record in self:
            if record.state in ['2', '3']:
                raise ValidationError('Cannot delete approved or settled records!')
        return super().unlink()

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

    goods_id = fields.Many2one('goods', string='Goods Name', required=True)
    package_id = fields.Many2one('package', string='Package', required=True)
    unit_price = fields.Char(string='Unit Price', default=0)
    quantity = fields.Char(string='Number', default=1)
    weight = fields.Float(string='Weight')
    volume = fields.Float(string='Volume')
    pricing_mode = fields.Selection(
        [('1', 'By Unit Price'),
         ('2', 'By Weight'),
         ('3', 'By Volume')],
        string='Pricing Mode', default="1")
    rates = fields.Many2one('rate', string='Rate')
    total_freight = fields.Float(string='Total Freight')

    waybill_id = fields.Many2one('waybill', string='Freight Information')

    @api.onchange('pricing_mode', 'volume', 'weight', 'quantity', 'unit_price', 'rates')
    def _onchange_to_total_freight(self):
        match self.pricing_mode:
            case "1":
                self.total_freight = self.unit_price
            case "2":
                self.total_freight = self.weight*self.rates.rate_value
            case "3":
                self.total_freight = self.volume*self.rates.rate_value
