from django.contrib import admin

# Register your models here.
from system.models import News, Slider, ImageFile
from utils.admin_actions import set_valid, set_invalid


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """新闻管理"""
    list_display = ('title','type','is_valid')
    actions = [set_valid,set_invalid]


@admin.register(Slider)
class NewsAdmin(admin.ModelAdmin):
    """轮播图管理"""
    list_display = ('name','start_time','end_time')
    actions = [set_valid,set_invalid]


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    """商品图片表"""
    list_display = ('summary','object_id','img','content_object','is_valid')