from django.contrib import admin
from .models import Post

# رجیستر کردن مدل
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'item_name', 'receiver_name', 'status', 'created_at']
    search_fields = ['tracking_code', 'item_name', 'receiver_name']
    list_filter = ['status', 'created_at']

