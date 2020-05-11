from django.conf.urls import url

from mall import views

urlpatterns = [
    # 商品列表  def function实现
    # url(r'^prod/list/$', views.product_list, name='product_list'),

    # 使用class实现分页
    url(r'^prod/list/$', views.ProductList.as_view(), name='product_list'),
    # 加载html片段的地址
    url(r'^prod/load/list/$', views.ProductList.as_view(
        template_name='product_load_list.html'
    ), name='product_load_list'),

    # 商品详情
    url(r'^prod/detail/(?P<pk>\S+)/$', views.product_detail, name='product_detail'),
    # 商品分类
    url(r'^prod/classify/$', views.prod_classify, name='prod_classify')
]
