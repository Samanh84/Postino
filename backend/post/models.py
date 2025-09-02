from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

class Post(models.Model):
    item_name = models.CharField(max_length=200, verbose_name="نام کالا")
    item_weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="وزن کالا (کیلوگرم)")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت کالا (تومان)")
    
    receiver_name = models.CharField(max_length=200, verbose_name="نام گیرنده")
    receiver_address = models.TextField(verbose_name="آدرس گیرنده")
    receiver_phone = models.CharField(max_length=15, verbose_name="شماره تماس گیرنده")

    # وضعیت‌ها به فارسی
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
        max_length=10, 
        unique=True, 
        default=generate_tracking_code,
        verbose_name="کد رهگیری"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ثبت شده توسط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return f"{self.item_name} - {self.tracking_code}"
