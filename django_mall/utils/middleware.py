from django.http import HttpResponse

from accounts.models import User


def ip_middleware(get_response):
    """中间件：ip拦截"""
    def middleware(request):

        # 请求到达前的业务逻辑
        # print("请求到达前的业务逻辑")
        # 请求不满足业务规则：Ip被限制
        ip = request.META.get('REMOTE_ADDR',None)
        ip_disable_list = [
            # '127.0.0.1'
        ]
        if ip in ip_disable_list:
            return HttpResponse('not allowed',status=403)
        response = get_response(request)
        # 在视图函数调用之后的业务逻辑
        # print('在视图函数调用之后的业务逻辑')
        return response

    return middleware


class MallAuthMiddleware(object):
    """ 自定义的登录验证中间件 """

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request,*args, **kwargs):
        # 请求到达前的业务逻辑
        # print("MallAuthMiddleware请求到达前的业务逻辑")
        user_id = request.session.get('user_id',None)
        if user_id:
            user = User.objects.get(pk=user_id)
        else:
            user = None

        request.my_user = user
        response = self.get_response(request)

        # 在视图函数调用之后的业务逻辑
        # print('MallAuthMiddleware在视图函数调用之后的业务逻辑')
        return response
