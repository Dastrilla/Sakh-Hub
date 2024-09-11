from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


from .models import Post, Group
from .forms import PostForm


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
    form = PostForm(request.POST or None)
    context = {"form":form}
    if not form.is_valid() or request.method != "POST":
        return render(request, "new_post.html", context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect("index")

def profile(request, username):
    profile = get_object_or_404(User, username = username)
    post_list = list(Post.objects
                     .all()
                     .select_related('author')
                     .filter(author__username = profile.username)
                     )
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {"profile":profile, "page":page, "paginator":paginator}

    return render (request, "profile.html", context)

def post_view(request, username, post_id):
    profile = get_object_or_404(User, username = username)
    post = get_object_or_404(Post, author__username = profile.username, id = post_id)
    posts = list(Post.objects
                 .all()
                 .select_related("author")
                 .filter(author__username = profile.username)
                 )

    context = {"post":post, "profile":profile}

    return render(request, "post.html", context)

@login_required(login_url="login")
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username = username, id = post_id)
    if request.user.username != post.author.username:
        return redirect("post", username=username, post_id = post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {"form":form, "post":post}
    if not form.is_valid() or request.method != "POST":
        return render(request, "new_post.html", context)
    form.save()
    return redirect('post', username=username, post_id = post_id)