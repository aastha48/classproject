from itertools import count

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView

from blog.forms import CommentForm, PostForm
from blog.models import Post, Comment


# def home(request):
#     object_list = Post.objects.order_by("-created_date")
#     count = object_list.count()
#     ctx = {
#         "object_list": object_list,
#         "count": count
#     }
#     return render(request, 'home.html', context=ctx)


def get_one_post(request, *args, **kwargs):
    arg = kwargs.get('pk')
    # one_post = Post.objects.get(pk=arg)
    one_post = get_object_or_404(Post, pk=arg)
    ctx = {
        "one_post": one_post
    }
    return render(request, 'blog/post_detail.html', context=ctx)


# def about(request):
#     return render(request, 'about.html', context={})

# def contact(request):
#     return render(request, 'contact.html', context={})


class HomeView(TemplateView):
    def get(self, request, *args, **kwargs):
        object_list = Post.objects.order_by("-created")
        count = object_list.count()
        ctx = {
            "object_list": object_list,
            "count": count,
        }
        return render(request, 'blog/home.html', context=ctx)


class ContactView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact.html', context={})


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'

    # Option 1
    #  queryset = Post.objects.filter(status='published').order_by('-created')

    # Option 2
    # def get_queryset(self):
    #     return Post.objects.order_by('-created_date')

    # Option 3
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        # context['object_list'] = Post.objects.order_by('-created')
        # context['object_list'] = Post.objects.filter(status='published').order_by('-created')
        context['object_list'] = Post.published.all()
        context['count'] = context['object_list'].count()
        return context


class PostDetailView(DetailView):
    # Old method
    # model = Post
    # context_object_name = 'one_post'
    # template_name = 'blog/post_detail.html'

    # def get_context_data(self, **kwargs):
    #     context = super(PostDetailView, self).get_context_data(**kwargs)
    #     context['comments'] = Comment.objects.all()
    #     return context

    # New method: To get post and the comments
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        # get one object
        one_post = Post.objects.get(pk=pk)

        # based on the object, get the comments in the post
        # comments = Comment.objects.filter(post_id=one_post)
        comments = one_post.post_comments.all()
        comment_form = CommentForm()

        # Prepare context
        ctx = {
            "one_post": one_post,
            'comments': comments,
            "comment_form": comment_form
        }
        return render(request, 'blog/post_detail.html', context=ctx)

    def post(self, request, *args, **kwargs):
        comments = CommentForm(data=request.POST)
        if comments.is_valid():
            new_comment = comments.save(commit=False)
            post_comment = get_object_or_404(Post, pk=kwargs.get('pk'))
            new_comment.post_id = post_comment
            new_comment.save()
            return redirect('blog:detail', pk=post_comment.pk)


def post(request):
    post_list = PostForm()
    ctx = {
        'post_list': post_list
    }
    if request.method == 'POST':
        com = PostForm(data=request.POST)
        com.save()
        return redirect('blog:home')
    else:
        pass
    return render(request, template_name='blog/new_post.html', context=ctx)




def search(request, *args, **kwargs):
    query = request.POST.get('searchquery')
    result = Post.objects.filter(Q(title__contains=query) | Q(body__contains=query)).filter(status="published")
    count = result.count()

    ctx = {
        'result': result,
        'count': count
    }
    return render(request, 'blog/searchresult.html', context=ctx)


@login_required
def new_post(request):
    if request.method == "POST":
        new_post_form = PostForm(request.POST)
        if new_post_form.is_valid():
            post = new_post_form.save(commit=False)
            post.author = request.user
            post.save()
            redirect('blog:post_detail', pk=new_post_form.pk)
    else:
        form = PostForm()
        return render(request, 'blog/new_post.html', {'form': form})
