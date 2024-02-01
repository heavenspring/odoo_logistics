from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Shipper(models.Model):
    _name = 'shipper'
    _description = 'Shipper'
    _rec_name = "shipper_name"

    shipper_name = fields.Char(string='Shipper Name', required=True)
    tel=fields.Char(string='Phone', required=True)

    
class receiver(models.Model):
    _name = 'receiver'
    _description = 'Receiver'
    _rec_name = "receiver_name"

    receiver_name = fields.Char(string='Consignee Name', required=True)
    tel=fields.Char(string='Phone', required=True)
    address=fields.Char(string='Address')
    