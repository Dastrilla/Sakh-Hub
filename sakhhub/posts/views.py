from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


from .models import Post, Group
from .forms import PostForm


def index(request):
    post_list = list(Post.objects
                     .order_by('-pub_date')
                     .all()
                     .select_related('author')
    )


    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug = slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    context = {"group":group, "posts":posts}

    return render(request, "group.html", context)


@login_required(login_url='login')
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid() or request.method != 'POST':
        return render(request, 'new_post.html', {'form':form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('index')