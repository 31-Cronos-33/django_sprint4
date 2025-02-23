from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)


from blog.models import Post, Category, Comment, User
from blog.forms import PostForm, CommentForm, ProfileForm


POSTS_LIMIT = 10


def filter_posts(posts, flag=True):
    queryset = posts.select_related(
        'author',
        'location',
        'category'
    )
    if flag:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    return queryset


def annotate_posts(posts):
    return posts.prefetch_related('comments').annotate(
        comment_count=Count('comments')
    ).order_by(
        Post._meta.ordering[0] if Post._meta.ordering else '-pub_date'
    )


class AuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin, AuthorMixin):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs[self.pk_url_kwarg]
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CommentMixin(LoginRequiredMixin):
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class IndexListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_LIMIT

    def get_queryset(self):
        return annotate_posts(filter_posts(Post.objects.all()))


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    paginate_by = POSTS_LIMIT
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            post = get_object_or_404(
                annotate_posts(filter_posts(Post.objects.all())),
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return post

    def get_queryset(self):
        return self.get_object().comments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = self.get_object()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryDetailView(ListView):
    template_name = 'blog/category.html'
    paginate_by = POSTS_LIMIT
    slug_url_kwarg = 'category_slug'

    def get_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True
        )

    def get_queryset(self):
        posts = self.get_object().posts.all()
        return annotate_posts(filter_posts(posts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class ProfileDetailView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = POSTS_LIMIT
    slug_url_kwarg = 'username'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg]
        )

    def get_queryset(self):
        posts = self.get_object().posts.all()
        flag = self.request.user != self.get_object()
        return annotate_posts(filter_posts(posts, flag))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostView(PostMixin, UpdateView):
    pass


class DeletePostView(PostMixin, DeleteView):
    pass


class CreateCommentView(CommentMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            annotate_posts(filter_posts(Post.objects.all())),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class EditCommentView(CommentMixin, AuthorMixin, UpdateView):
    form_class = CommentForm


class DeleteCommentView(CommentMixin, AuthorMixin, DeleteView):
    pass


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
