from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView

from mall.models import Product
from mine.models import Order, Cart
from utils import constants, tools


@login_required
def index(request):
    """个人中心"""
    return render(request,'mine.html',{
        'constants':constants
    })


class OrderDetailView(DetailView):  # 显示一个特定类型对象的详细信息
    """订单详情"""
    model = Order
    slug_field = 'sn'  # 根据模型的sn字段进行查询。
    slug_url_kwarg = 'sn'  # 从url获取条件pk的别名是sn
    template_name = 'order_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['constants'] = constants
        return context


@login_required      # 未登陆不能执行
@transaction.atomic()        # 自动控制
def cart_add(request, prod_uid):
    """添加商品到购物车"""
    user = request.user
    product = get_object_or_404(Product, uid=prod_uid,
                                is_valid=True,
                                status=constants.PRODUCT_STATUS_SELL)
    # 购买数量
    count = int(request.POST.get('count', 1))
    # 校验库存
    if product.remain_count < count:
        return HttpResponse('no')
    # 减库存
    product.update_store_count(count)
    # 生成购物车记录
    # 如果已经添加到购物车，就购买数量和价格更新
    try:
        cart = Cart.objects.get(product=product, user=user,
                                status=constants.ORDER_STATUS_INIT)
        count = cart.count + count
        cart.count = count
        cart.amount = count * cart.price
        cart.save()
    except Cart.DoesNotExist:
        # 没有加入到过购物车
        Cart.objects.create(
            product=product,
            user=user,
            name=product.name,
            img=product.img,
            price=product.price,
            origin_price=product.origin_price,
            count=count,
            amount=count * product.price
        )
    return HttpResponse('ok')


@login_required
def cart(request):
    """我的购物车"""
    """购物车中的商品列表"""
    user = request.user
    shop_total=None
    prod_list = user.cart.filter(status=constants.ORDER_STATUS_INIT)
    # print('购物车列表:',prod_list)
    # 购物车结算总额
    shop_total = prod_list.aggregate(Sum('amount'))
    print('总额：',shop_total)
    # 聚合查询

    if request.method == 'POST':
        # 提交订单
        # 1.保存用户的地址快照
        default_addr = user.default_addr
        if not default_addr:
            # 消息通知
            messages.warning(request,'请选择地址信息')
            return redirect('account:address_list')
        # 订单总额计算
        cart_total = prod_list.aggregate(sum_amount=Sum('amount'),sum_count=Sum('count'))
        # print(cart_total)
        order = Order.objects.create(
            user=user,
            sn=tools.gen_trans_id(),
            buy_amount=cart_total['sum_amount'],
            buy_count=cart_total['sum_count'],
            to_user=default_addr.username,
            to_area=default_addr.get_region_format(),
            to_address=default_addr.address,
            to_phone=default_addr.phone
        )
        # 2.修改购物车中的状态， 已经提交
        # 3.生成订单，关联到购物车
        prod_list.update(
            status=constants.ORDER_STATUS_SUBMIT,order=order
        )
        # 4.跳转到订单详情
        messages.success(request,'下单成功，请支付')
        return redirect('mine:order_detail',order.sn)

    return render(request,'cart.html',{
            'prod_list':prod_list,
            'shop_total':shop_total

    })


@login_required
def order_pay(request):
    """提交订单"""
    user = request.user
    if request.method == 'POST':
        sn = request.POST.get('sn',None)
        # 1.查询订单信息
        order = get_object_or_404(Order,sn=sn,user=user,status=constants.ORDER_STATUS_SUBMIT)
        # 2.验证余额够不够
        if order.buy_amount > user.integral:
            messages.error(request,'您的积分余额不足')
            return redirect('mine:order_detail', sn=sn)
        # 3.钱扣掉
        user.ope_integral_account(0,order.buy_amount)       # types不为0则扣钱(减法)
        # 4.修改订单状态
        order.status = constants.ORDER_STATUS_PAIED
        order.save()
        # 5.修改购物车关联的状态
        order.carts.all().update(status=constants.ORDER_STATUS_PAIED)
        messages.success(request,'支付成功')
    return redirect('mine:order_detail', sn=sn)


# @login_required
# def order_list(request):
#     """我的订单列表"""
#     status = request.GET.get('status','')
#     try:
#         status = int(status)
#     except ValueError:
#         status = ''
#     return render(request,'order_list.html',{
#         'constants': constants,
#         'status': status,
#     })


@login_required
def prod_collect(request):
    """我的收藏"""
    return render(request,'prod_collect.html',{

    })


class OrderListView(ListView):
    """基于类视图的订单列表"""
    model = Order    # 关联的模型
    template_name = 'order_list.html'   # 关联的模块

    def get_queryset(self):
        """查询订单"""
        status = self.request.GET.get('states','')
        user = self.request.user    # 当前登录的用户
        query = Q(user=user)
        if status:        # 如果接收到订单状态
            query = query & Q(status=status)
        return Order.objects.filter(query).exclude(   # 排除用户已经删除的订单
            status=constants.ORDER_STATUS_DELETED
        )

    def get_context_data(self, **kwargs):
        # 重写上下文
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status','')
        try:
            status = int(status)
        except ValueError:
            status = ''
        context['status'] = status
        context['constants'] = constants
        return context
