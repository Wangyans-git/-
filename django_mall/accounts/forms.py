import re

from django import forms
from django.contrib.auth import authenticate, login

from accounts.models import User, UserAddress
from utils.verify import VerifyCode


class UserLoginForm(forms.Form):
    """用户登录表单"""
    username = forms.CharField(label='用户名:', max_length=64)
    password = forms.CharField(label='密码:', max_length=64, widget=forms.PasswordInput,
                               error_messages={
                                   'required': '请输入密码'
                               })
    verify_code = forms.CharField(label='验证码:', max_length=4, error_messages={
        'required': '请输入验证码'
    })

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # def clean_username(self):
    #     """验证用户名 钩子函数"""
    #     username = self.cleaned_data['username']
    #     print(username)     # 获取username的值
    #     # 判断用户名是否为手机号码
    #     pattern = r'^0{0,1}1[0-9]{10}$'
    #     if not re.search(pattern,username):
    #         raise forms.ValidationError('请输入正确的手机号码')
    #     return username

    def clean_verify_code(self):
        """验证用户输入的验证码是否正确"""
        verify_code = self.cleaned_data['verify_code']
        if not verify_code:
            raise forms.ValidationError('请输入验证码')
        client = VerifyCode(self.request)
        if not client.validate_code(verify_code):
            raise forms.ValidationError('你输入的验证码不正确')
        return verify_code

    def clean(self):
        """验证用户名和密码"""
        cleaned_data = super().clean()
        print(cleaned_data)
        """获取用户名和密码，不建议使用[]的方法"""
        # username = cleaned_data['username']    # 可能拿不到值

        username = cleaned_data.get('username', None)  # 取不到值，就取得None
        password = cleaned_data.get('password', None)
        if username and password:
            """查询用户名是否存在"""
            user_list = User.objects.filter(username=username)
            if user_list.count() == 0:
                raise forms.ValidationError('用户名不存在')
            """认证用户"""
            if not authenticate(username=username, password=password):
                raise forms.ValidationError('密码错误')
        return cleaned_data


class UserRegisterForm(forms.Form):
    """用户注册表单"""
    username = forms.CharField(label='用户名', max_length=64)
    nickname = forms.CharField(label='昵称', max_length=32,)
    password = forms.CharField(label='密码', max_length=64, widget=forms.PasswordInput)
    password_repeat = forms.CharField(label='重复密码', max_length=64, widget=forms.PasswordInput)
    verify_code = forms.CharField(label='验证码', max_length=4)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_username(self):
        """验证用户名是否被注册"""
        date = self.cleaned_data['username']
        if User.objects.filter(username=date).exists():
            raise forms.ValidationError('用户名已存在')
        return date

    def clean_verify_code(self):
        """验证用户输入的验证码是否正确"""
        verify_code = self.cleaned_data['verify_code']
        if not verify_code:
            raise forms.ValidationError('请输入验证码')
        client = VerifyCode(self.request)
        if not client.validate_code(verify_code):  # 判断
            raise forms.ValidationError('你输入的验证码不正确')
        return verify_code

    # 判断两次密码是否相同
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', None)
        password_repeat = cleaned_data.get('password_repeat', None)
        if password and password_repeat:
            if password != password_repeat:
                raise forms.ValidationError('两次密码不一致')
        return cleaned_data

    def register(self):
        """注册的方法"""
        data = self.cleaned_data
        # 1.创建用户
        User.objects.create_user(username=data['username'], password=data['password'],nickname=data['nickname'])
        # 2.自动登录
        user = authenticate(username=data['username'], password=data['password'])
        # 调用login函数登陆用户
        login(self.request, user)
        return user


# class UserForm(forms.ModelForm):
#     """从模型创建表单"""
#
#     class Meta:
#         model = User
#         fields = ['username','password','nick']
#         # 界面显示表单输入
#         widgets = {
#             'password':forms.PasswordInput(attrs={
#                 'class':'text-error'
#             }),  # 密码框
#         }
#         # 修改显示文字
#         labels = {
#             'username':'手机号码'
#         }
#         error_messages = {
#             'required':'请输入手机号码',
#             'max_length':'最长不超过32位'
#         }


class UserAddressForm(forms.ModelForm):
    """地址新增或修改"""
    region = forms.CharField(label='大区域选项', max_length=64, required=True,
                             error_messages={
                                 'required': '请选择地址'  # 错误的提示消息
                             })

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    class Meta:
        model = UserAddress
        fields = ['address', 'username', 'phone', 'is_default']
        widgets = {
            'is_default':forms.CheckboxInput(attrs={
                'class':'weui-switch'
            })
        }

    def clean_phone(self):
        """验证是否为手机号"""
        phone = self.cleaned_data['phone']
        pattern = r'^0{0,1}1[1-9]{10}$'
        if not re.search(pattern, phone):
            raise forms.ValidationError('请输入正确的手机号码')
        return phone

    def clean(self):
        cleaned_date = super().clean()
        # 查询当前登录用户的地址数据
        addr_list = UserAddress.objects.filter(is_valid=True,user=self.request.user)   # 满足该条件的。。当前用户的列表
        if addr_list.count() >= 20:
            raise forms.ValidationError('最多只能添加20个地址')
        return cleaned_date

    def save(self,commit=True):    # 保存方法
        obj = super().save(commit=False)
        region = self.cleaned_data['region']      # 当前省市区
        (province,city,area) = region.split(' ')    # 接收当前省市区数据，并用空格进行分割
        obj.province = province    # 模型关联
        obj.city = city
        obj.area = area
        obj.user = self.request.user

        # 修改的时候，如果已经有了默认地址，当前页勾选了默认地址选项
        # 需要把之前的地址都改为非默认的地址
        if self.cleaned_data['is_default']:
            UserAddress.objects.filter(is_valid=True,user=self.request.user,
                                       # 把之前的地址都改为非默认的地址
                                       is_default=True).update(is_default=False)
        obj.save()