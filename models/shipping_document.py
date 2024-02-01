from odoo import models, fields, api
from odoo import tools
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import ValidationError


class ShippingDocument(models.Model):
    _name = 'shipping.document'
    _description = 'Shipping Document'

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
        return f'CY{local_date.strftime("%Y%m%d")}{record_count + 1:04d}'
    
    shipping_num_auto = fields.Char(string='Shipping Number', default=generate_custom_code, readonly=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    destination = fields.Many2one('city', string='Destination', required=True)
    driver_id = fields.Many2one('driver', string='Driver', required=True)
    shipping_cost = fields.Float(string='Shipping Cost')
    goods_total_freight = fields.Float(string='Goods Total Freight', compute='_compute_total_freight')
    
    detail_ids = fields.One2many('shipping.document.detail', 'shipping_document_id', string='Shipping Document Detail')
    state = fields.Selection([('1','Draft'),
                              ('2','Confirmed'),
                              ('3','Settled')], default='1', string="Status")
    
    
    def action_confirm(self):
        status='2'      
        select_des=dict(self.env['trail'].fields_get(allfields=['status'])['status']['selection']).get(status, '')
        for item in self.detail_ids:
            trail_vals = {
                'waybill_id': item.waybill_id.id,
                'status': status,
                'description':select_des
            }
            trail = self.env['trail'].create(trail_vals)  
        self.state='2'

        
    def action_cancel(self):
        ids= self.detail_ids.mapped('waybill_id').ids
        self.env['trail'].search([('waybill_id', 'in', ids),('status', '=', '2')]).unlink()
        self.state = '1'


    def unlink(self):
        for record in self:
            if record.state in ['2', '3']:
                raise ValidationError('Cannot delete approved or settled records!')
        return super().unlink()





    # 重载name_get()方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s" % (record.shipping_num_auto)
            result.append((record.id, rec_name))
        return result
    
    @api.depends('detail_ids.total_fees')
    def _compute_total_freight(self):
        for shipping_document in self:
            shipping_document.goods_total_freight = sum(shipping_document.detail_ids.mapped('total_fees'))
            
    @api.onchange('destination')
    def _onchange_shipper_id(self):
        if self.destination:
            domain = [('destination', '=', self.destination.id),('state', '=', 2)]
            #查询所有已审核运单
            waybill_confirmed_ids = self.env['waybill'].search(domain).ids
            #查询承运明细表中已存在的未审核运单
            waybill_used_ids=self.env['shipping.document.detail'].search([('waybill_id','in',waybill_confirmed_ids)]).mapped('waybill_id').ids
            #两者取差集
            result = [x for x in waybill_confirmed_ids if x not in waybill_used_ids]
            #编辑状态下的逻辑
            waybill_exit_id=self.env['shipping.document.detail'].search([('shipping_document_id','=',self.ids),('destination_id','=',self.destination.id)]).mapped('waybill_id').ids
            result=sorted(list(dict.fromkeys(result + waybill_exit_id)))#取并集升序排列

            self.write({'detail_ids': [(5, 0, 0)]})
            child_records = [(0, 0, {'waybill_id': record}) for record in result]
            self.detail_ids = child_records

       

class ShippingDocumentDetail(models.Model):
    _name = 'shipping.document.detail'
    _description = 'Shipping Document Detail'

    waybill_id = fields.Many2one('waybill', required=True, domain="[('state', '=', 2),('id', 'not in', used_waybill_ids),('destination', '=', destination_id)]")
    receiver_id = fields.Many2one(related='waybill_id.receiver_id', readonly=True)
    receiver_tel = fields.Char(string="Consignee Phone", store=False, readonly=True, compute="_compute_customerInfo")
    detail_ids = fields.One2many(related='waybill_id.detail_ids')
    total_fees = fields.Float(related='waybill_id.total_fees')
    waybill_create_date=fields.Datetime(related='waybill_id.create_date')
    shipping_document_id = fields.Many2one('shipping.document', string='Shipping Document',ondelete='cascade')
    used_waybill_ids = fields.Many2many('waybill', compute='_compute_used_waybill_ids')
    destination_id=fields.Many2one('city', compute="_compute_destination_id",store=True)
     
    
    @api.depends('receiver_id')
    def _compute_customerInfo(self):
        for customer in self:
            customer.receiver_tel = customer.receiver_id.tel           

    
    

    @api.depends('shipping_document_id.destination')
    def _compute_destination_id(self):   
        if self.shipping_document_id.destination:
            self.destination_id=self.shipping_document_id.destination
    
    @api.onchange('waybill_id')
    def _compute_used_waybill_ids(self):
        domain = [('destination', '=', self.shipping_document_id.destination.id),('state', '=', 2)]
        waybill_confirmed_ids = self.env['waybill'].search(domain).ids
        waybill_used_ids=self.search([('waybill_id','in',waybill_confirmed_ids)]).mapped('waybill_id').ids
        #编辑状态下的逻辑
        waybill_exit_id=self.search([('shipping_document_id','=',self.shipping_document_id.ids),('destination_id','=',self.shipping_document_id.destination.id)]).mapped('waybill_id').ids
        result =[x for x in waybill_used_ids if x not in waybill_exit_id] #取差集升序排列

        waybill_exit_ids=self.shipping_document_id.detail_ids.mapped('waybill_id').ids
        result=sorted(list(dict.fromkeys(result + waybill_exit_ids)))
      

        self.used_waybill_ids = result
    
        
