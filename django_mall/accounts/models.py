from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


# class User(models.Model):   # 继承django自带的用户模型
from django.db.models import F


class User(AbstractUser):     # 对用户模型进行扩展
    """用户的基础信息表"""
    # username = models.CharField('用户名',max_length=64)
    # password = models.CharField('密码',max_length=255)
    avatar = models.ImageField('头像',upload_to='avatar',null=True)
    integral = models.IntegerField('用户积分',default=0)
    nickname = models.CharField('昵称',max_length=32)
    level = models.SmallIntegerField('用户等级',default=0)

    class Meta:
        db_table = 'acounts_user'
        verbose_name = '用户基础信息'
        verbose_name_plural = '用户基础信息'

    @property
    def default_addr(self):
        """用户的默认地址，多个地方用到"""
        addr = None
        user_list = self.user_address.filter(is_valid=True)
        # UserAddress.objects.filter(user=user,is_valid=True)
        # 1.找到默认地址
        try:
            addr = user_list.filter(is_default=True)[0]
        # 2.如果没有默认就使用第一个
        except IndexError:
            try:
                addr = user_list[0]
            except IndexError:
                pass
        return addr

    def ope_integral_account(self,types,count):
        """积分操作"""
        if types == 1:
            # 充值
            self.integral = F('integral') + abs(count)
        else:
            # 消费
            self.integral = F('integral') - abs(count)
        self.save()
        self.refresh_from_db()     # 更新数据库

    # def __str__(self):
    #     return self.username


class UserProfile(models.Model):
    """用户详细信息"""
    SEX_CHOICES = (
        (1, '男'),
        (0, '女'),
    )
    user = models.OneToOneField(User)      # 关联用户基础信息表
    real_name = models.CharField('真实姓名',max_length=32)
    email = models.CharField('邮箱',max_length=128,null=True,blank=True)
    is_email = models.BooleanField('邮箱是否已经验证注册',default=False)
    phone = models.CharField('电话号码',max_length=20,null=True,blank=True)
    is_phone = models.BooleanField('手机号是否验证',default=False)
    sex = models.SmallIntegerField('性别',default=1,choices=SEX_CHOICES)
    age = models.SmallIntegerField('年龄',default=0)

    creat_at = models.DateTimeField('创建时间',auto_now_add=True)
    update_at = models.DateTimeField('修改时间',auto_now=True)

    class Meta:
        db_table = 'account_user_profile'
        verbose_name = '用户详细信息'
        verbose_name_plural = '用户详细信息'


class UserAddress(models.Model):
    """用户的地址信息"""
    user = models.ForeignKey(User,related_name='user_address')
    province = models.CharField('省份',max_length=32)
    city = models.CharField('城市',max_length=32)
    area = models.CharField('区域',max_length=32)
    town = models.CharField('街道',max_length=32,null=True,blank=True)

    address = models.CharField('详细地址',max_length=64)
    username = models.CharField('收件人',max_length=32)
    phone = models.CharField('收件人电话,',max_length=20)

    is_default = models.BooleanField('是否为默认地址',default=False)
    is_valid = models.BooleanField('是否有效',default=True)

    created_at = models.DateTimeField('创建时间',auto_now_add=True)
    updated_at = models.DateTimeField('修改时间',auto_now=True)

    class Meta:
        db_table = 'account_user_address'
        ordering = ['is_default','-updated_at']
        verbose_name = '用户地址'
        verbose_name_plural = '用户地址'

    def get_phone_format(self):
        """格式化手机号码"""
        return self.phone[0:3]+'****' + self.phone[7:]

    def get_region_format(self):
        """格式化省市区"""
        return '{self.province} {self.city} {self.area}'.format(self=self)

    def __str__(self):
        return self.get_region_format() + self.address


class LoginRecord(models.Model):
    """用户的登陆历史"""
    user = models.ForeignKey(User)
    username = models.CharField('登陆的账号',max_length=64)
    ip = models.CharField('登陆的ip',max_length=32)
    address = models.CharField('登陆的地址',max_length=32,null=True,blank=True)
    source = models.CharField('登陆的来源',max_length=32)

    created_at = models.DateTimeField('登陆的时间',auto_now = True)

    class Meta:
        db_table = 'accounts_login_record'


class PasswordChangeLog(models.Model):
    """用户的密码修改历史"""
    pass