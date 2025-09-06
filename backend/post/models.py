from django.db import models
from django.contrib.auth.models import User
import random
import string

# generate unique tracking code
def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

class Post(models.Model):
    item_name = models.CharField(max_length=200, verbose_name="نام کالا")
    item_weight = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="وزن کالا (کیلوگرم)")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ارزش قیمت کالا (تومان)")

    receiver_name = models.CharField(max_length=200, verbose_name="نام گیرنده")
    receiver_address = models.TextField(verbose_name="آدرس گیرنده")
    receiver_phone = models.CharField(max_length=15, verbose_name="شماره تماس گیرنده")  #  +98

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

    # Weight in kg and g
    def weight_kg_g(self):
        total_grams = int(round(self.item_weight * 1000))
        kg = total_grams // 1000
        g = total_grams % 1000
        parts = []
        if kg > 0:
            parts.append(f"{kg} کیلوگرم")
        if g > 0:
            parts.append(f"{g} گرم")
        return " و ".join(parts) if parts else "0 گرم"

    # Normalize phone to E.164 format for storage only
    def save(self, *args, **kwargs):
        if self.receiver_phone:
            phone = self.receiver_phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if phone.isdigit() and len(phone) == 10:
                self.receiver_phone = f"+98{phone}"
            elif phone.startswith("0") and len(phone) == 11:
                self.receiver_phone = f"+98{phone[1:]}"
            elif phone.startswith("98") and not phone.startswith("+98"):
                self.receiver_phone = f"+{phone}"
            elif phone.startswith("+98") and len(phone) == 13:
                self.receiver_phone = phone
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.tracking_code}"
