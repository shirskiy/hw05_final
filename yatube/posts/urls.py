
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.new_post, name='new_post'),
    path('about/', include('about.urls', namespace='about')),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/', views.post_edit, name='post_edit'
    ),
    path(
        '<username>/<int:post_id>/comment/',
        views.add_comment, name='add_comment'
    ),
]