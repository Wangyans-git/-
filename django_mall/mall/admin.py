from django.contrib import admin

# Register your models here.
from mall.forms import ProductAdminForm
from mall.models import Product, Classify, Tag

# 方式1.注册到admin管理
from utils.admin_actions import set_invalid, set_valid


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """商品信息管理"""
    # 在列表中显示的字段
    list_display = ('name','type','price','status','is_valid')
    # 修改分页数据的大小
    list_per_page = 5
    list_filter = ('status',)    # 数组
    actions = [set_invalid,set_valid]

    # 排除掉某些字段，使其不能被编辑，但不可见
    # exclude = ['remain_count']
    # 不能编辑，但是可见
    readonly_fields = ['remain_count']
    # 自定义的表单
    form = ProductAdminForm

    def __str__(self):
        return self.name

# 方式2.注册到admin管理
# admin.site.register(Product,ProductAdmin)


@admin.register(Classify)
class ClassifyAdmin(admin.ModelAdmin):
    """商品分类"""
    list_display = ('uid','name','desc')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """商品标签"""
    list_display = ('name','uid','creat_at','is_valid')


