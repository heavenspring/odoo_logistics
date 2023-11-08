from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Shipper(models.Model):
    _name = 'shipper'
    _description = 'Shipper'
    _rec_name = "shipper_name"

    shipper_name = fields.Char(string='发货人', required=True)
    tel=fields.Char(string='电话', required=True)
    
class receiver(models.Model):
    _name = 'receiver'
    _description = 'Receiver'
    _rec_name = "receiver_name"

    receiver_name = fields.Char(string='收货人', required=True)
    tel=fields.Char(string='电话', required=True)
    address=fields.Char(string='收货地址')
    