from django import forms
from .models import Post

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
