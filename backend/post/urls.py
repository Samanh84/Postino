from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .auth_forms import EmailLoginForm

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_post, name='create_post'),
    path('signup/', views.signup, name='signup'),
    path('track/', views.track_post, name='track_post'),
    path('track/<str:tracking_code>/', views.track_post, name='track_post'),
    path('my_posts/', views.my_posts, name='my_posts'),

    # login and logout
    path('login/', auth_views.LoginView.as_view(
        template_name='post/login.html',
        authentication_form=EmailLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]
