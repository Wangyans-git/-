from datetime import datetime
import logging
from django.shortcuts import render_to_response, render

# from accounts.models import User
from mall.models import Product
from system.models import Slider, News
from utils import constants

logger = logging.getLogger('index')


def index(request):
    """首页"""
    # 记录调试信息
    logger.debug('调试信息')
    logger.info('普通信息')
    logger.error('异常信息')

    # 查询轮播图
    sliter_list = Slider.objects.filter(types=constants.SLIDER_TYPE_INDEX)     # constants在数据库中查询的条件

    # 首页的新闻
    now_time = datetime.now()
    news_list = News.objects.filter(type=constants.NEWS_TYPE_NEW,
                                    is_top=True,                # 置顶的
                                    is_valid=True,              # 删除的
                                    start_time__lte=now_time,     # 小于等于
                                    end_time__gte=now_time          # 大于等于
                                    )
    # 酒水推荐
    js_list = Product.objects.filter(
        status=constants.PRODUCT_STATUS_SELL,
        is_valid=True,
        tags__code='jstj'
    )
    # 精选推荐
    jx_list = Product.objects.filter(
        status=constants.PRODUCT_STATUS_SELL,
        is_valid=True,
        tags__code='jstj'
    )
    # 猜你喜欢
    xh_list = Product.objects.filter(
        status=constants.PRODUCT_STATUS_SELL,
        is_valid=True,
        tags__code='cnxh'
    )
    # # 从session中获取用户id
    # user_id = request.session[constants.LOGIN_SESSION_ID]
    # print(user_id)
    # # 查询当前登录的用户
    # user = User.objects.get(pk=user_id)
    return render(request,'index.html',{
        'slider_list':sliter_list,
        'news_list':news_list,
        # 'user':user,
        'js_list':js_list,
        'jx_list':jx_list,
        'xh_list':xh_list
    })

