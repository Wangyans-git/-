from django.db.models import Sum

from utils import constants


def shop_cart(request):
    """ 当前用户的购物车信息"""
    user = request.user
    cart_list = []   # 购物车状态的商品
    cart_total = {}    # 购物车中的商品数量和商品总价
    cart_count = 0    # 数量可能为0(没有购物车状态的商品)
    if user.is_authenticated:
        # 我的购物车商品列表
        cart_list = user.cart.filter(
            status=constants.ORDER_STATUS_INIT
        )
        cart_total = cart_list.aggregate(sum_amount=Sum('amount'),
                                         sum_count=Sum('count'))
        cart_count = cart_list.count
    return {
            'cart_list':cart_list,
            'cart_total':cart_total,
            'cart_count':cart_count,
    }
