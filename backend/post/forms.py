from django import forms
from .models import Post
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "item_name",
            "item_weight",
            "item_price",
            "receiver_name",
            "receiver_address",
            "receiver_phone",
        ]

    def clean_receiver_phone(self):
        phone = self.cleaned_data.get('receiver_phone', '').strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # 10-digit local number
        if phone.isdigit() and len(phone) == 10:
            return f"+98{phone}"
        elif phone.startswith("0") and len(phone) == 11:
            return f"+98{phone[1:]}"
        elif phone.startswith("98") and not phone.startswith("+98"):
            return f"+{phone}"
        elif phone.startswith("+98") and len(phone) == 13:
            return phone
        else:
            raise ValidationError('.شماره تماس معتبر نیست! باید 10 رقم باشد')
