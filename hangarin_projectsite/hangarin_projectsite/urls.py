"""
URL configuration for hangarin_projectsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks.views import (
    HomePageView, TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    PriorityListView, PriorityCreateView, PriorityUpdateView, PriorityDeleteView # <-- Add these three!
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('', HomePageView.as_view(), name='home'),
    path('accounts/', include('allauth.urls')),
    
    # Task URLs
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/add/', TaskCreateView.as_view(), name='task-add'),
    path('tasks/<pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    
    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category-add'), # <-- New!
    path('categories/<pk>/', CategoryUpdateView.as_view(), name='category-update'), # <-- New!
    path('categories/<pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'), # <-- New!
    
    # Priority URLs
    path('priorities/', PriorityListView.as_view(), name='priority-list'),
    path('priorities/add/', PriorityCreateView.as_view(), name='priority-add'),
    path('priorities/<pk>/', PriorityUpdateView.as_view(), name='priority-update'),
    path('priorities/<pk>/delete/', PriorityDeleteView.as_view(), name='priority-delete'),

]