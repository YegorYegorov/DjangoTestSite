from django.shortcuts import render, get_object_or_404, redirect
from .models import News, Category, Comment
from .forms import NewsForm, UserRegisterForm, UserLoginForm, ContactForm, CommentForm
from django.views.generic import ListView, DetailView, CreateView
from .utils import MyMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.http import Http404, HttpResponse


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    return render(request, "news/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, "news/login.html", {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


class HomeNews(MyMixin, ListView):
    paginate_by = 5
    model = News
    template_name = 'news/home_list_news.html'
    context_object_name = 'news'
    # mixin_prop = 'hello world'
    extra_context = {
        'title': 'Главная'
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        # context['mixin_prop'] = self.get_prop()
        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category')


class GetCategory(ListView):
    model = News
    template_name = 'news/home_list_news.html'
    context_object_name = 'news'
    allow_empty = False
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True, category_id=self.kwargs['category_id']).select_related('category')


class ViewNews(DetailView):
    model = News
    # pk_url_kwarg = 'news_id'
    context_object_name = 'news_item'

    def get_pk_news(self):
        return News.objects.get('pk')

    def get_queryset(self):
        return News.objects.filter(is_published=True)


class CreateNews(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = 'news/add-news.html'


def test(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'], 'mezzagora@gmail.com',
                             ['pullowski@gmail.com'], fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('test')
            else:
                messages.error(request, 'Ошибка отправки письма')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = ContactForm()
    return render(request, "news/test.html", {"form": form})


def post_detail_view(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(News, pk=pk)
        comments = Comment.objects.filter(active=True)
        csubmit = False
        if request.method == 'POST':
            form = CommentForm(data=request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.post = post
                new_comment.save()
                csubmit = True
                return redirect('view_news', pk)
        else:
            form = CommentForm()
        return render(request, 'news/comment.html',
                      {'post': post, 'comments': comments, 'csubmit': csubmit, 'form': form})
    else:
        messages.error(request, 'Вы не авторизованы')
        return redirect('home')

# def index(request):
#     news = News.objects.order_by('-created_at')
#     context = {
#         'news': news,
#         'title': 'Список новостей',
#     }
#     return render(request, 'news/index.html', context)


# def get_category(request, category_id):
#     news = News.objects.filter(category_id=category_id)
#     category = Category.objects.get(pk=category_id)
#     context = {
#         'news': news,
#         'category': category,
#     }
#
#     return render(request, 'news/category.html', context)


# def view_news(request, news_id):
#     news_item = get_object_or_404(News, pk=news_id, is_published=True)
#     context = {
#         'news_item': news_item,
#     }
#     return render(request, 'news/view_news.html', context)


# def add_news(request):
#     if request.method == 'POST':
#         form = NewsForm(request.POST)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             # news = News.objects.create(**form.cleaned_data)
#             news = form.save()
#             return redirect(news)
#     else:
#         form = NewsForm()
#     return render(request, 'news/add-news.html', {'form': form,})
