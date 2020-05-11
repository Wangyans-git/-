import os
import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import HttpResponse


class VerifyCode(object):
    """验证码"""
    def __init__(self,dj_request):
        self.dj_request = dj_request
        # 验证码大小
        self.img_width = 100
        self.img_height = 30
        # 验证码长度
        self.code_len = 4

        # django中session的名称
        self.session_key = 'verify_code'

    def gen_code(self):
        """生成验证码"""
        # 1.使用随机数生成随机验证码
        code = self.get_vcode()
        print(code)
        # 2.把验证码存在session
        self.dj_request.session[self.session_key] = code
        # 3.准备随机元素（背景颜色，验证码文字的颜色，干扰性）
        font_color = ['red','blue','green','yellow']
        # RGB随机背景色
        bg_color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
        # 字体路径
        font_path = os.path.join(settings.BASE_DIR,'static','fonts','timesbi.ttf')

        # 创建图片
        img = Image.new('RGB', (self.img_width, self.img_height), bg_color)
        draw = ImageDraw.Draw(img)   # 画笔

        # 画干扰线
        # 随机条数
        for i in range(random.randrange(1,int(self.code_len / 2)+1)):
            line_color = random.choice(font_color)
            # 点的坐标位置
            # point = (0,0,self.img_width,self.img_height)
            point = (
                random.randrange(0, self.img_width * 0.2),
                random.randrange(0,self.img_height),
                random.randrange(self.img_width*0.8,self.img_width),
                random.randrange(0,self.img_height)
                )
            # 线条的宽度
            width = random.randrange(1, 4)
            draw.line(point, fill=line_color, width=width)

        # 画验证码
        for index,char in enumerate(code):
            code_color = random.choice(font_color)
            # 指定字体
            font_size = random.randrange(15,25)
            font = ImageFont.truetype(font_path,font_size)
            point = (index * self.img_width/self.code_len,
                     random.randrange(0,self.img_height/3))       # 字体坐标
            draw.text(point,char,font=font,fill=code_color)       # 画验证码

        buf = BytesIO()
        img.save(buf,'gif')       # 保存到图中
        return HttpResponse(buf.getvalue(),'image/gif')

    def get_vcode(self):
        """生成随机验证码"""
        random_str = 'ABCDEFGHIJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
        code_list = random.sample(list(random_str),self.code_len)
        code = ''.join(code_list)   # 拼接
        return code

    def validate_code(self,code):
        """验证验证码是否正确"""
        # 1.转变大小写
        code = str(code).lower()   # 转换成小写
        vcode = self.dj_request.session.get(self.session_key,'')    # 没有获取到就为空字符串
        return vcode.lower() ==code


# if __name__ == '__main__':
#     client = VerifyCode(None)
#     client.gen_code()