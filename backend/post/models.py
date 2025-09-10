from django.db import models
from django.contrib.auth.models import User
import random
import string
from decimal import Decimal, ROUND_HALF_UP

# تولید کد رهگیری
def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="استان")

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="شهر")
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name="استان"
    )

    class Meta:
        unique_together = ('name', 'province')
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"

    def __str__(self):
        return f"{self.name} ({self.province.name})"


class Post(models.Model):
    item_name = models.CharField(max_length=200, verbose_name="نام کالا")
    item_weight = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="وزن کالا (کیلوگرم)")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ارزش قیمت کالا (تومان)")

    receiver_name = models.CharField(max_length=200, verbose_name="نام گیرنده")
    receiver_address = models.TextField(verbose_name="آدرس گیرنده")
    receiver_phone = models.CharField(max_length=15, verbose_name="شماره تماس گیرنده")

    origin_province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="origin_posts",
        verbose_name="استان مبدأ",
        null=True, blank=True
    )
    origin_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="origin_posts",
        verbose_name="شهر مبدأ",
        null=True, blank=True
    )
    destination_province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="destination_posts",
        verbose_name="استان مقصد",
        null=True, blank=True
    )
    destination_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="destination_posts",
        verbose_name="شهر مقصد",
        null=True, blank=True
    )

    STATUS_CHOICES = [
        ("registered", "ثبت در سیستم"),
        ("in_transit", "رهسپار مقصد"),
        ("arrived", "رسیده به استان/شهر"),
        ("delivered", "تحویل داده شد"),
        ("canceled", "لغو شد"),
    ]
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="registered",
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

    def save(self, *args, **kwargs):
        # نرمال‌سازی شماره تلفن
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

    def weight_display(self):
        """نمایش هوشمند وزن به فارسی"""
        weight = self.item_weight  # DecimalField

        if weight < Decimal('1'):
            grams = int((weight * 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            return f"{grams} گرم"

        kilos = int(weight)
        grams = int(((weight - Decimal(kilos)) * 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

        if grams == 0:
            return f"{kilos} کیلوگرم"
        else:
            return f"{kilos} کیلو {grams} گرم"

    def __str__(self):
        return f"{self.item_name} - {self.get_status_display()} - {self.tracking_code}"


class PostStatusHistory(models.Model):
    STATUS_CHOICES = [
        ("registered", "ثبت در سیستم"),
        ("in_transit", "رهسپار مقصد"),
        ("arrived", "رسیده به استان/شهر"),
        ("delivered", "تحویل داده شد"),
        ("canceled", "لغو شد"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="history", verbose_name="مرسوله")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name="استان")
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="شهر")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ و ساعت")

    class Meta:
        verbose_name = "تاریخچه وضعیت پست"
        verbose_name_plural = "تاریخچه وضعیت پست‌ها"

    def status_text(self):
        """تولید متن فارسی هوشمند برای وضعیت‌ها"""
        if self.status == "in_transit":
            if self.post.destination_province:
                if self.post.destination_city:
                    return f"رهسپار {self.post.destination_province.name} / {self.post.destination_city.name} شد"
                return f"رهسپار {self.post.destination_province.name} شد"
            return "رهسپار مقصد شد"
        elif self.status == "delivered":
            if self.post.destination_province:
                if self.post.destination_city:
                    return f"تحویل گیرنده در {self.post.destination_province.name} / {self.post.destination_city.name}"
                return f"تحویل گیرنده در {self.post.destination_province.name}"
            return "تحویل گیرنده"
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def __str__(self):
        if self.city:
            return f"{self.post.tracking_code} - {self.province.name} / {self.city.name} - {self.status_text()}"
        return f"{self.post.tracking_code} - {self.province.name} - {self.status_text()}"
