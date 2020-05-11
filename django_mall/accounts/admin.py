from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, UserProfile, UserAddress


# 注册到admin管理
@admin.register(User)    # 因为已经定制用户，所以继承UserAdmin
class UserAdmin(UserAdmin):
    """用户基础信息"""
    # 用户管理
    list_display = ('format_username','nickname','integral','is_active')
    fieldsets = (
        (None,{'fields':('username','password')}),
        (('用户详细信息'), {'fields':
                         ('first_name','last_name','email','integral','avatar','level')}),
        (('用户状态信息'), {'fields':
                         ('is_active','is_staff','is_superuser','date_joined','last_login')})
    )

    # 支持按用户名和昵称搜索
    search_fields = ('username','nickname')
    # 添加自定义的方法
    actions = ['disable_user','enable_user']

    def format_username(self,obj):
        """用户名脱敏处理"""
        return obj.username[0:3] + '***'
    format_username.short_description = '用户名'       # 修改列名显示

    def disable_user(self,request,queryset):
        """定义批量禁用选中的用户操作函数"""
        queryset.update(is_active=False)
    disable_user.short_description = '批量禁用用户'

    def enable_user(self,request,queryset):
        """定义批量启用选中的用户操作函数"""
        queryset.update(is_active=True)
    enable_user.short_description = '批量启用用户'


""""配置admin，使用django自带用户模型"""
# admin.site.register(User,UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户详细信息"""
    list_display = ('user','phone','email')


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """用户地址"""
    list_display = ('user','address','username','phone')
    search_fields = ('user__username','user__nickname','user_phone')