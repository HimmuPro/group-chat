from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/create-user/', views.create_user, name='create_user'),
    path('api/edit-user/<str:username>/', views.edit_user, name='edit_user'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('groups/', views.groups, name='groups'),
    path('groups/create/', views.create_group, name='create-group'),
    path('groups/search/', views.search_groups, name='search-groups'),
    path('groups/<slug:slug>/', views.group, name='group'),
    path('groups/<slug:slug>/delete/', views.delete_group, name='delete-group'),
    path('groups/<slug:slug>/group-users/', views.group_users, name='group-users'),
    path('groups/<slug:slug>/add-members/', views.add_members, name='add-members'),
]
