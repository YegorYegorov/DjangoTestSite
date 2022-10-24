from django import template
from news.models import Category
from django.db.models import Count, Sum

register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories


@register.inclusion_tag('news/list_categories.html')
def show_categories():
    # categories = Category.objects.all()
    categories = Category.objects.filter(news__is_published=True).annotate(cnt=Count('news__is_published'))
    return {"categories": categories}
