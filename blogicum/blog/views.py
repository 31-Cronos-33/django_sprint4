from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import Http404


from .models import Category, Post


POSTS_LIMIT = 5


def get_published_posts():
    return Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')


def index(request):
    template_name = 'blog/index.html'
    post_list = get_published_posts()[:POSTS_LIMIT]
    context = {'post_list': post_list}
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'
    try:
        post = get_object_or_404(get_published_posts(), pk=id)
    except Http404:
        raise Http404('Страница не найдена')
    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    try:
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
    except Http404:
        raise Http404('Страница не найдена')
    post_list = get_published_posts().filter(category=category)
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template_name, context)
