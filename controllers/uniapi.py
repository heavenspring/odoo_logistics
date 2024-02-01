import logging
from odoo import http
from odoo.tools import config
from odoo.exceptions import UserError, AccessError, AccessDenied
import json
import requests

_logger = logging.getLogger(__name__)

#odoo 控制器方法拦截
def custom_decorator(func):
    # *args代表可变的tuple类型参数；**kwargs代表可变的dict类型参数
    def wrapper(*args, **kwargs):
        # Custom logic before executing the controller method
        json_data = http.request.params
        print("Custom decorator: Before executing the controller method")
        result = func(*args, **kwargs)  # Execute the controller method
        # Custom logic after executing the controller method
        print("Custom decorator: After executing the controller method")
        return result
    return wrapper

class Uniapi(http.Controller):#继承 odoo.http.Controller以通过Odoo路由系统注册该控制器


    @http.route('/api/erp/login', type='json', auth='none', cors='*', methods=['POST'],csrf=False)
    def login(self,account,pwd):
        result = {
            'success': True,
            'message': '登录成功！',
            'code':200,
            'data':''
        }
        # 获取当前请求的域名
        current_domain = http.request.httprequest.host_url
        # current_domain = 'https://wuliu.gardenengineer.club'
        json_data = http.request.params
        url= "%s/web/session/authenticate" % current_domain
        _logger.info("current_domain: %s", current_domain)
        data = {
            "params": {
                "db": "erp",
                "login": account,
                "password": pwd,
            }
        }
        headers = {'Content-type': 'application/json'}
        try:
            response = requests.post(url, headers=headers,json=data)
            session_id=response.cookies["session_id"]
            if session_id:
                result['data']={"session_id":session_id,"userinfo":{"account":json_data['account'],"age":20}}
            else:
                result['message']='用户名或密码错误！'
                result['success']=False
        except KeyError:
            error_data = {'error': 'Authentication failed or session expired'}
            result['message']='用户名或密码错误！'
            result['success']=False           
        return result
    
    @http.route('/api/erp/test', type='json', auth='user', cors='*')
    @custom_decorator
    def custom_api_endpoint(self,*args, **kwargs):
        result = {
            'success': True,
            'message': 'Hello from custom API!',
            'code':200
        }
        return result