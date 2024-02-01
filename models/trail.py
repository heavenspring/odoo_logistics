from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Trail(models.Model):
    _name = 'trail'
    _description = 'Trail'

    
    departure_station=fields.Many2one('city',string='Departure Station')
    destination_station=fields.Many2one('city',string='Destination Station')
    waybill_id = fields.Many2one('waybill')
    type = fields.Selection([('1','Through'),
                              ('2','Transfer')], string="Type")
    stay_type=fields.Selection([('1','Arrive'),
                              ('2','Send to')],string="Stay Type")
    status = fields.Selection(
        [('1', 'Ordered'),
         ('2', 'To Be Sent'),
         ('3', 'In Transit'),
         ('4', 'Delivery'),
         ('5', 'Have Been Signed')],
        string='Status', default="1")
    
    description=fields.Char(string='Description')
    
    def get_status_display_name(self):
        return self.status.get_display_name()
    
    @api.onchange('departure_station', 'destination_station', 'type', 'stay_type', 'status')
    def _onchange_to_description(self):
        select_des=dict(self.fields_get(allfields=['status'])['status']['selection']).get(self.status, '')
        select_stay_type=dict(self.fields_get(allfields=['stay_type'])['stay_type']['selection']).get(self.stay_type, '')
        select_type=dict(self.fields_get(allfields=['type'])['type']['selection']).get(self.type, '')
        match self.status:
            case "1":
                self.description =select_des
            case "2":
                self.description = select_des
            case "3":
                description = "【%s】" % (self.departure_station.city_name)
                match self.stay_type:
                    case "1":
                        self.description = "【%s】%s" % (self.destination_station.city_name, select_stay_type)
                    case "2":
                        self.description = "【%s】%s【%s】" % (self.departure_station.city_name, select_stay_type,self.destination_station.city_name)
                        match self.type:
                            case "2":
                               self.description = "【%s】%s【%s】%s" % (self.departure_station.city_name, select_stay_type,self.destination_station.city_name,select_type)
            case "4":
                self.description = select_des
            case "5":
                self.description = select_des


