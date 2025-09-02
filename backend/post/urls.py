from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_post, name='create_post'),
    path('signup/', views.signup, name='signup'),

    # مسیر پیگیری پست با ارسال کد رهگیری
    path('track/', views.track_post, name='track_post'),  # بدون tracking_code
    path('track/<str:tracking_code>/', views.track_post, name='track_post'),  # با tracking_code

    
    # پنل کاربران برای مشاهده پست‌های خود و ادمین
    path('my_posts/', views.my_posts, name='my_posts'),

    # ورود و خروج
    path('login/', auth_views.LoginView.as_view(template_name='post/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]
