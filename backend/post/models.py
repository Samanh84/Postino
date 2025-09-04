from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.core.exceptions import ValidationError


# generate unique tracking code
def generate_tracking_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return code


class Post(models.Model):
    item_name = models.CharField(max_length=200, verbose_name="نام کالا")
    item_weight = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="وزن کالا (کیلوگرم)")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ارزش قیمت کالا (تومان)")

    receiver_name = models.CharField(max_length=200, verbose_name="نام گیرنده")
    receiver_address = models.TextField(verbose_name="آدرس گیرنده")
    receiver_phone = models.CharField(max_length=15, verbose_name="شماره تماس گیرنده")  # همیشه +98...

    # status
    STATUS_CHOICES = [
        ('در حال پردازش', 'در حال پردازش'),
        ('ارسال شد', 'ارسال شد'),
        ('تحویل داده شد', 'تحویل داده شد'),
        ('لغو شد', 'لغو شد'),
    ]
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='در حال پردازش',
        verbose_name="وضعیت پست"
    )

    tracking_code = models.CharField(
        max_length=12,
        unique=True,
        default=generate_tracking_code,
        verbose_name="کد رهگیری"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ثبت شده توسط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    # Weight kg and g
    def weight_kg_g(self):
        total_grams = int(self.item_weight * 1000)
        kg = total_grams // 1000
        g = total_grams % 1000
        if kg and g:
            return f"{kg} کیلوگرم و {g} گرم"
        elif kg:
            return f"{kg} کیلوگرم"
        elif g:
            return f"{g} گرم"
        else:
            return "0 گرم"

    # نرمال‌سازی شماره تلفن به E.164
    def normalize_phone(self, phone: str) -> str:
        phone = phone.strip().replace(" ", "").replace("-", "")

        if phone.isdigit() and len(phone) == 10:
            return f"+98{phone}"
        elif phone.startswith("0") and len(phone) == 11:
            return f"+98{phone[1:]}"
        elif phone.startswith("98") and not phone.startswith("+98"):
            return f"+{phone}"
        elif phone.startswith("+98"):
            return phone
        else:
            raise ValidationError({
                'receiver_phone': 'شماره تماس معتبر نیست. باید با 09 یا 98 یا +98 شروع شود یا 10 رقم خام باشد.'
            })

    # override save برای نرمال‌سازی شماره تلفن
    def save(self, *args, **kwargs):
        if self.receiver_phone:
            self.receiver_phone = self.normalize_phone(self.receiver_phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.tracking_code}"
