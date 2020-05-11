from django import forms

from mall.models import Product


class ProductAdminForm(forms.ModelForm):
    """ 商品编辑 """

    class Meta:
        model = Product
        exclude = ['creat_at','updated_at']
        widgets = {
            # 修改表单输入界面为单选按钮
            'type': forms.RadioSelect
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        print(price)
        if int(price) <= 0:
            raise forms.ValidationError('销售价格不能小于0')
        return price
