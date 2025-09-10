from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .auth_forms import CustomUserCreationForm, EmailLoginForm
from .forms import PostForm
from .models import Post, Province, PostStatusHistory   # ← اینجا اصلاح شد


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
            messages.success(request, '.ثبت‌نام با موفقیت انجام شد! خوش آمدید')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'post/signup.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()

            # ایجاد اولین رکورد تاریخچه
            PostStatusHistory.objects.create(
                post=post,
                province=post.destination_province,
                status="registered"
            )

            messages.success(request, f'پست شما با موفقیت ثبت شد! کد رهگیری: {post.tracking_code}')
            return render(request, 'post/post_success.html', {'tracking_code': post.tracking_code})
    else:
        form = PostForm()
    return render(request, 'post/post_create.html', {'form': form})


def track_post(request, tracking_code=None):
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
    if request.user.is_superuser:
        posts = Post.objects.all().order_by('-created_at')
    else:
        posts = Post.objects.filter(created_by=request.user).order_by('-created_at')

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        new_status = request.POST.get('status')
        try:
            post = Post.objects.get(id=post_id)
            if request.user.is_superuser or post.created_by == request.user:
                post.status = new_status
                post.save()

                # اضافه کردن تاریخچه جدید
                PostStatusHistory.objects.create(
                    post=post,
                    province=post.destination_province,
                    status="arrived" if new_status == "ارسال شد" else (
                        "delivered" if new_status == "تحویل داده شد" else "in_transit"
                    )
                )

                messages.success(request, f'وضعیت پست {post.tracking_code} به "{new_status}" تغییر کرد.')
            else:
                messages.error(request, '.شما اجازه تغییر وضعیت این پست را ندارید')
        except Post.DoesNotExist:
            messages.error(request, '.پست مورد نظر یافت نشد')
        return redirect('my_posts')

    return render(request, 'post/my_posts.html', {'posts': posts})
