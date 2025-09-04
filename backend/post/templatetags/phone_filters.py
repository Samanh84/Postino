from django import template

register = template.Library()

@register.filter
def format_phone(value):
    """
    شماره تلفن +989118182753 را به 09118182753 تبدیل می‌کند
    """
    if not value:
        return ""
    value = value.strip()
    # اگر با +98 شروع می‌شود، صفر اضافه می‌کنیم
    if value.startswith("+98"):
        value = "0" + value[3:]
    # اگر با 98 شروع می‌شود بدون +، صفر اضافه می‌کنیم
    elif value.startswith("98"):
        value = "0" + value[2:]
    # اگر با 0 شروع می‌شود، همان‌طور بماند
    return value
