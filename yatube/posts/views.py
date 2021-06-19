from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    else:
        context = {
            'form': form,
            'title': 'Новая запись',
            'button': 'Опубликовать'
        }
        return render(request, 'new.html', context)


def profile(request, username):
    poster = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=poster)
    num_posts = user_posts.count()
    paginator = Paginator(user_posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = ''
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=poster).exists()
    followers = Follow.objects.filter(author=poster).count()
    followed = Follow.objects.filter(user=poster).count()
    context = {'poster': poster,
               'page': page,
               'num_posts': num_posts,
               'following': following,
               'followers': followers,
               'followed': followed,
               }
    return render(
        request,
        'profile.html',
        context
    )


def post_view(request, username, post_id):
    poster = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    num_posts = Post.objects.filter(author__username=username).count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'comments': comments,
        'poster': poster,
        'post': post,
        'num_posts': num_posts,
        'comment': Comment.objects.filter(post=post),
        'form': form,
    }
    return render(
        request,
        'post.html',
        context
    )


@login_required
def post_edit(request, username, post_id):
    author_id = get_object_or_404(User, username=username).id
    if request.user.id != author_id:
        return redirect('post', username, post_id)

    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    context = {
        'form': form,
        'title': 'Редактировать запись',
        'button': 'Изменить запись',
        'post': post,
    }
    return render(
        request,
        'new.html',
        context
    )


def page_not_found(request, exeptption):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    context = {
        'form': form
    }
    return render(request, 'includes/comments.html', context)


@login_required
def follow_index(request):
    user = request.user
    followed_posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(followed_posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page
    }
    return render(
        request,
        'follow.html',
        context
    )


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('profile', username=author)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('profile', username)
