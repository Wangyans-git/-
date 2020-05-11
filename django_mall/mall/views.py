from django.db.models import Q
from django.shortcuts import render,get_object_or_404


# Create your views here.
from django.views.generic import ListView

from mall.models import Product
from utils import constants


def product_list(request, template_name='product_list.html'):
    # 商品列表
    # 展示的商品列表需要的条件
    prod_list = Product.objects.filter(status=constants.PRODUCT_STATUS_SELL,
                                       is_valid=True)
    # 按名称搜索
    name = request.GET.get('name','')
    if name:
        prod_list = prod_list.filter(name__icontains=name)
    return render(request, template_name,{
        'prod_list':prod_list
    })


def product_detail(request, pk, template_name='product_detail.html'):
    """商品详情"""
    prod_obj = get_object_or_404(Product, uid=pk,is_valid=True)          # uid是随机字符串，不容易被爬取数据
    user = request.user
    default_addr = None
    if user.is_authenticated:
        default_addr = user.default_addr
    return render(request, template_name, {
            'prod_obj': prod_obj,
            'default_addr':default_addr
    })


class ProductList(ListView):       # 获取数据表中的所有数据，返回一个列表
    """商品列表"""
    # 每页放多少数据
    paginate_by = 5
    # 模块位置
    template_name = 'product_list.html'

    def get_queryset(self):
        query = Q(status=constants.PRODUCT_STATUS_SELL,is_valid=True)
        # 按名称搜索
        name = self.request.GET.get('name','')
        if name:
            query = query & Q(name__icontains=name)

        # 按标签进行搜索
        tag = self.request.GET.get('tag','')
        if tag:
            query = query & Q(tags__code=tag)

        # 按照分类进行搜索
        cls = self.request.GET.get('cls','')
        if cls:
            query = query & Q(classes__code=cls)
        return Product.objects.filter(query)

    def get_context_data(self, **kwargs):
        """ 添加变量到上下文 """
        context = super().get_context_data(**kwargs)
        context['params'] = self.request.GET.dict()
        return context


def prod_classify(request):
    """商品分类"""
    return render(request,'prod_classify.html',{

    })