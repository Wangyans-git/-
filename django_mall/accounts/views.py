from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout

# Create your views here.
from accounts.forms import UserLoginForm, UserRegisterForm, UserAddressForm
from accounts.models import User, UserAddress
from utils import constants
from utils.verify import VerifyCode


def user_login(request):
    """用户登录"""
    # 第一次访问URL展示表单，GET供用户输入
    # 如果登陆是从其他页面跳转过来的，会带next参数，如果有next参数，登录完成后，需要跳转到next
    # 所对应的地址，否则调到首页上去
    next_url = request.GET.get('next', 'index')
    # 第一次访问URL展示表单，POST
    if request.method == 'POST':
        form = UserLoginForm(request=request,data=request.POST)
        client = VerifyCode(request)    # 调用验证码
        code = request.POST.get('verify_code',None)       # 前台获取的vcode值
        print('验证码：',code)
        rest = client.validate_code(code)         # 验证结果
        print("验证结果:",rest)
        # print(request.POST)
        # 验证是否通过验证
        if form.is_valid():
            #   执行登录
            print('验证通过')
            # 返回验证后的表单数据
            data = form.cleaned_data
            # # 查询用户名信息
            # user = User.objects.get(username=data['username'],password=data['password'])
            # request.session[constants.LOGIN_SESSION_ID] = user.id      # 查询结果设置到session中去
            #
            # return redirect('index')         # 登录后调转到首页

            """使用django-auth来实现登录"""
            user = authenticate(request,username=data['username'],password=data['password'])
            if user is not None:
                # 在视图中获取当前用户
                login(request,user)
                # 登录后的跳转
                print('next_url:',next_url)
                return redirect(next_url)
        else:
            print(form.errors)

    else:
        # get 请求，展示我们的页面
        form = UserLoginForm(request)
    return render(request,'login.html',{
        'form': form,
        'next_url': next_url
    })


def user_logout(request):
    """用户退出"""
    logout(request)
    return redirect('index')


def user_register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegisterForm(request=request, data=request.POST)
        if form.is_valid():
            # 调用注册方法
            print("注册成功")
            form.register()
            return redirect('index')
        else:
            print('注册失败：',form.errors)
    else:
        form = UserRegisterForm(request=request)
    return render(request,'register.html',{
        'form':form
    })


@login_required
def address_list(request):
    """地址列表"""
    my_addr_list = UserAddress.objects.filter(user=request.user,is_valid=True)
    print(my_addr_list)
    return render(request,'address_list.html',{
        'my_addr_list':my_addr_list
    })


@login_required
def address_edit(request,pk):
    """新增或编辑地址"""
    user = request.user   # user对象
    addr = None
    initial = {}
    # 如果pk是数字，则表示修改
    if pk.isdigit():
        # 查询相关的地址信息
        addr = get_object_or_404(UserAddress,pk=pk,user=user, is_valid=True)
        initial['region'] = addr.get_region_format()
    if request.method == 'POST':
        form = UserAddressForm(request=request,data=request.POST,initial=initial,instance=addr)
        if form.is_valid():
            form.save()
            return redirect('accounts:address_list')
    else:
        form = UserAddressForm(request=request,instance=addr,initial=initial)
    return render(request,'address_edit.html',{
            'form':form
    })


def address_delete(request,pk):
    """删除地址"""
    addr = get_object_or_404(UserAddress,pk=pk,is_valid=True,user=request.user)
    addr.is_valid = False
    addr.save()
    return HttpResponse('ok')