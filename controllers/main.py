import logging
from odoo import http
from odoo.tools import config
from odoo.http import request
from odoo.exceptions import UserError, AccessError, AccessDenied
import json
import requests

_logger = logging.getLogger(__name__)


class Main(http.Controller):#继承 odoo.http.Controller以通过Odoo路由系统注册该控制器


    @http.route('/api/erp/get_waybill_list', type='json', auth='user', cors='*')
    def get_waybill_list(self,keyword,startTime,endTime):
        result = {
            'success': True,
            'message': '执行成功！',
            'code':200,
            'data':''
        }     
        try:
            # 获取当前用户时区
            tz_name = http.request.env.user.tz

            waybill = request.env['waybill'].search(['|',('goods_num_auto', 'like', keyword),('receiver_id.receiver_name', 'like', keyword),('receiver_tel', 'like', keyword)],order='id desc', limit=20)
            waybill_data=waybill.mapped(lambda x: {
            'id': x.id,
            'goods_num_auto': x.goods_num_auto,
            'receiver': x.receiver_id.receiver_name,
            'receiver_tel': x.receiver_tel,
            'receiver_address': x.receiver_address,
            'details': [{'id': y.id, 'good': y.goods_id.goods_name}
                            for y in x.detail_ids]
        })
            result['data']=waybill_data
        except KeyError:
            error_data = {'error': 'Authentication failed or session expired'}
            result['message']='内部错误！'
            result['success']=False           
        return result
    