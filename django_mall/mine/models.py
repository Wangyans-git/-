from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# Create your models here.
from accounts.models import User
from mall.models import Product
from system.models import ImageFile
from utils import constants

"""
购物流程
1.查看商品
2.加入购物车
3.选择购物车中商品并下单（选择收货地址，是否开发票）
4.支付
5.确认收货
"""


class Order(models.Model):
    """订单模型"""
    sn = models.CharField('订单编号',max_length=32)
    user = models.ForeignKey(User,related_name='order')
    buy_count = models.IntegerField('购买数量',default=1)
    buy_amount = models.FloatField('购买总价')

    to_user = models.CharField('收货人',max_length=32)
    to_area = models.CharField('省市区',max_length=32)
    to_address = models.CharField('详细地址',max_length=32)
    to_phone = models.CharField('收货人电话',max_length=32)

    remark = models.CharField('备注',max_length=255,null=True,blank=True)

    # 快递信息
    express_type = models.CharField('快递',max_length=32,null=True,blank=True)
    express_no = models.CharField('快递单号',max_length=32,null=True,blank=True)

    status = models.SmallIntegerField('订单状态',default=constants.ORDER_STATUS_SUBMIT,
                                      choices=constants.ORDER_STATUS_CHOICES)

    class Meta:
        db_table = 'mine_order'
        verbose_name = '订单列表'
        verbose_name_plural = '订单管理'

    def get_cart_products(self):
        """购物车中已下单的商品"""
        # 排除还在购物车状态的商品
        cart_pro = self.carts.exclude(status=constants.ORDER_STATUS_INIT)
        print(cart_pro)
        return cart_pro


class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey(User,related_name='cart')
    product = models.ForeignKey(Product)
    order = models.ForeignKey(Order,verbose_name='关联订单',null=True,related_name='carts')
    # 商品快照
    name = models.CharField('商品名称',max_length=128)
    img = models.ImageField('商品的主图')
    price = models.IntegerField('兑换价格')
    origin_price = models.FloatField('原价')

    count = models.PositiveIntegerField('购买数量')
    amount = models.FloatField('购买总额')

    status = models.SmallIntegerField('状态',choices=constants.ORDER_STATUS_CHOICES,
                                      default=constants.ORDER_STATUS_INIT)

    creat_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        db_table = 'mine_cart'
        verbose_name = '购物车'
        verbose_name_plural = '购物车'


class Comments(models.Model):
    """ 商品评价 """
    # 评分的维度
    # 匿名
    # 置顶，排序
    # 评论内容
    # 关联图片
    product = models.ForeignKey(Product, related_name='comments', verbose_name='商品')
    user = models.ForeignKey(User, related_name='comments', verbose_name='用户')
    order = models.ForeignKey(Order,related_name='comments',verbose_name='订单')
    desc = models.CharField('评价内容', max_length=256)
    reorder = models.SmallIntegerField('排序', default=0)
    is_anonymous = models.BooleanField('是否匿名', default=True)

    score = models.FloatField('商品评分', default=10.0)
    score_deliver = models.FloatField('配送服务分', default=10.0)
    score_package = models.FloatField('快递包装分', default=10.0)
    score_speed = models.FloatField('送货速度分', default=10.0)

    is_valid = models.BooleanField('是否有效', default=True)
    img_list = GenericRelation(ImageFile,
                               verbose_name='评价晒图',
                               related_query_name="img_list")

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        db_table = 'mine_product_comments'
        verbose_name = '商品评价'
        verbose_name_plural = '商品评价'
