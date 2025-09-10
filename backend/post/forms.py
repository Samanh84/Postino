from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Province, City


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "item_name",
            "item_weight",
            "item_price",
            "receiver_name",
            "origin_province",
            "origin_city",
            "destination_province",
            "destination_city",
            "receiver_address",
            "receiver_phone",
        ]
        widgets = {
            "origin_province": forms.Select(attrs={"class": "form-select"}),
            "origin_city": forms.Select(attrs={"class": "form-select"}),
            "destination_province": forms.Select(attrs={"class": "form-select"}),
            "destination_city": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # استان‌ها همیشه لود میشن
        self.fields["origin_province"].queryset = Province.objects.all()
        self.fields["destination_province"].queryset = Province.objects.all()

        # شهرها پیش‌فرض خالی می‌مونن
        self.fields["origin_city"].queryset = City.objects.none()
        self.fields["destination_city"].queryset = City.objects.none()

        # اگر استان انتخاب شده باشه → شهرهای مربوطه رو لود کن
        if "origin_province" in self.data:
            try:
                province_id = int(self.data.get("origin_province"))
                self.fields["origin_city"].queryset = City.objects.filter(province_id=province_id).order_by("name")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.origin_province:
            # وقتی فرم edit میشه
            self.fields["origin_city"].queryset = self.instance.origin_province.cities.order_by("name")

        if "destination_province" in self.data:
            try:
                province_id = int(self.data.get("destination_province"))
                self.fields["destination_city"].queryset = City.objects.filter(province_id=province_id).order_by("name")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.destination_province:
            self.fields["destination_city"].queryset = self.instance.destination_province.cities.order_by("name")

    def clean_receiver_phone(self):
        phone = (
            self.cleaned_data.get("receiver_phone", "")
            .strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        if phone.isdigit() and len(phone) == 10:
            return f"+98{phone}"
        elif phone.startswith("0") and len(phone) == 11:
            return f"+98{phone[1:]}"
        elif phone.startswith("98") and not phone.startswith("+98"):
            return f"+{phone}"
        elif phone.startswith("+98") and len(phone) == 13:
            return phone
        else:
            raise ValidationError("📵 شماره تماس معتبر نیست! باید 10 یا 11 رقم باشد")
