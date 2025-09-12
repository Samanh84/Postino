from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .auth_forms import CustomUserCreationForm
from .forms import PostForm
from .models import Post, Province, City, PostStatusHistory


def index(request):
    if request.method == 'POST':
        tracking_code = request.POST.get('tracking_code')
        return redirect('track_post', tracking_code=tracking_code)
    return render(request, 'post/index.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🌸 ثبت‌نام با موفقیت انجام شد! خوش آمدید ')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'post/signup.html', {'form': form})


@login_required
def create_post(request):
    """ایجاد پست جدید"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()

            # Started With Registered after creat Post! (ثبت در سیستم)
            PostStatusHistory.objects.create(
                post=post,
                province=post.origin_province,
                city=post.origin_city,
                status="registered"
            )

            # Success Screen for create post
            return render(request, 'post/post_success.html', {
                'tracking_code': post.tracking_code
            })
    else:
        form = PostForm()
    return render(request, 'post/post_create.html', {'form': form})


def track_post(request, tracking_code=None):
    """رهگیری پست با کد رهگیری"""
    post = None
    status = None
    history = None

    if tracking_code is None and request.method == 'POST':
        tracking_code = request.POST.get('tracking_code')

    if tracking_code:
        try:
            post = Post.objects.get(tracking_code=tracking_code)
            status = post.status
            history = post.history.order_by("created_at")
        except Post.DoesNotExist:
            status = 'not_found'

    return render(request, 'post/track_post.html', {
        'post': post,
        'status': status,
        'tracking_code': tracking_code,
        'history': history
    })


@login_required
def my_posts(request):
    """مدیریت پست‌های کاربر یا ادمین"""
    if request.user.is_superuser:
        posts = Post.objects.all().order_by('-created_at')
    else:
        posts = Post.objects.filter(created_by=request.user).order_by('-created_at')

    provinces = Province.objects.prefetch_related('cities').all()

    if request.method == 'POST':

        # Add History in Management panel
        if 'add_history' in request.POST:
            post_id = request.POST.get('post_id')
            province_id = request.POST.get('new_province')
            city_id = request.POST.get('new_city')
            status = request.POST.get('new_status')

            if post_id and province_id and status:
                try:
                    post = Post.objects.get(id=post_id)
                    province = Province.objects.get(id=province_id)
                    city = City.objects.get(id=city_id) if city_id else None

                    PostStatusHistory.objects.create(
                        post=post,
                        province=province,
                        city=city,
                        status=status
                    )
                    messages.success(request, f'مرحله جدید برای پست {post.tracking_code} ثبت شد.')
                except (Post.DoesNotExist, Province.DoesNotExist, City.DoesNotExist):
                    messages.error(request, 'پست یا استان/شهر انتخاب‌شده معتبر نیست')
            return redirect('my_posts')

        # Change status box in Management panel
        elif 'status' in request.POST:
            post_id = request.POST.get('post_id')
            new_status = request.POST.get('status')
            try:
                post = Post.objects.get(id=post_id)
                if request.user.is_superuser or post.created_by == request.user:
                    post.status = new_status
                    post.save()
                    messages.success(request, f'وضعیت پست {post.tracking_code} به "{new_status}" تغییر کرد.')
                else:
                    messages.error(request, 'شما اجازه تغییر وضعیت این پست را ندارید')
            except Post.DoesNotExist:
                messages.error(request, 'پست مورد نظر یافت نشد')
            return redirect('my_posts')

        # Delete Post
        elif 'delete_post_id' in request.POST:
            post_id = request.POST.get('delete_post_id')
            try:
                post = Post.objects.get(id=post_id)
                tracking_code = post.tracking_code
                post.delete()
                messages.success(request, f'پست {tracking_code} حذف شد.')
            except Post.DoesNotExist:
                messages.error(request, 'پست مورد نظر یافت نشد')
            return redirect('my_posts')

    return render(request, 'post/my_posts.html', {
        'posts': posts,
        'provinces': provinces
    })
