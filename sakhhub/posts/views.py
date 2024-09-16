from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


from .models import Post, Group, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


def index(request):
    post_list = list(Post.objects
                     .order_by("-pub_date")
                     .all()
                     .select_related("author")
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    context = {"page":page, "paginator":paginator}

    return render(request, 'index.html', context)

def groups(request):
    group_list = list(Group.objects.all())

    return render(request, 'groups.html', {'groups':group_list})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug = slug)
    post_list = list(Post.objects
                     .filter(group=group)
                     .order_by("-pub_date")
                     .select_related("group","author")
                     )
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    context = {"group":group, "page":page, "paginator":paginator}

    return render(request, "group.html", context)

@login_required(login_url="login")
def new_post(request):
    context = {"title":"Новая публикация", "button":"Опубликовать"}
    form = PostForm(request.POST or None)
    if not form.is_valid() or request.method != "POST":
        return render(request, "new_post.html", {"context":context, "form":form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect("index")

def profile(request, username):
    profile = get_object_or_404(User, username = username)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=profile).exists()
    post = list(Post.objects
                     .all()
                     .select_related('author')
                     .filter(author__username = profile.username)
                     )
    
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {"profile":profile, "page":page, "paginator":paginator, "following":following}

    return render (request, "profile.html", context)

def post_view(request, username, post_id):
    profile = get_object_or_404(User, username = username)
    post = get_object_or_404(Post, author__username = profile.username, id = post_id)
    posts = list(Post.objects
                 .all()
                 .select_related("author")
                 .filter(author__username = profile.username)
                 )

    form = CommentForm()
    items = post.comments.all()
    paginator = Paginator(posts, 10)

    return render(request, "post.html", {"post":post, "profile":profile, "paginator":paginator, "form":form,"items":items})

@login_required(login_url="login")
def post_edit(request, username, post_id):
    context = {"title":"Редактирование записи", "button":"Сохранить"}
    post = get_object_or_404(Post, author__username = username, id = post_id)
    if request.user.username != post.author.username:
        return redirect("post", username=username, post_id = post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if not form.is_valid() or request.method != "POST":
        return render(request, "new_post.html", {"context":context, "form":form, "post":post})
    form.save()
    return redirect('post', username=request.user.username, post_id = post_id)

def page_not_found(request, exception):

    context = {"path":request.path}
    return render(request, "misc/404.html", context, status=404)

def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required(login_url='login')
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username = username, id = post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid() or request.method != 'POST':
        return render(request, "comments.html", {"form":form, "post":post})
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect("post", username=username, post_id = post_id)

@login_required(login_url='login')
def follow_index(request):

    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {"page":page, "paginator":paginator})

@login_required(login_url='login')
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    if follow_author != request.user and (not request.user.follower.filter(author=follow_author).exists()):
        Follow.objects.create(
            user = request.user,
            author = follow_author
        )
    return redirect('profile', username=username)

@login_required(login_url='login')
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author = follow_author)
    if data_follow.exists():
        data_follow.delete()
    return redirect('profile', username)