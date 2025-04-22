import django_filters
from .models import *
from django.db.models import Q


class ClassFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    # teacher_name = django_filters.CharFilter(method='filter_by_teacher_name', label='Teacher Name')
    
    class Meta:
        model = Class
        fields = {
            'access_code': ['exact'],
        }

    '''def filter_by_teacher_name(self, queryset, name, value):
        return queryset.filter(
            Q(created_by__first_name__icontains=value) | 
            Q(created_by__last_name__icontains=value)
        )'''
    

class QuizFiltter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')

    class Meta:
        model = Quiz
        fields = {
            'access_code' : ['exact'],
        }


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username' : ['exact']
        }


class NotesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    class Meta:
        model = Notes
        fields = {
            'access_code' : ['exact']
        }


class BooksFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    class Meta:
        model = Notes
        fields = {
            'access_code' : ['exact']
        }

class BooksFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    class Meta:
        model = Book
        fields = {
            'author' : ['icontains'],
            'isbn' : ['exact'],
            'access_code' : ['exact']
        }
    

