from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('profile/', views.update_profile, name='update_profile'),
    path('search/', views.user_search, name='user_search'),
    path('start_chat/<int:profile_id>/', views.start_or_resume_chat, name='start_or_resume_chat'),
    path('set_last_chat/<int:chat_id>/', views.set_last_chat, name='set_last_chat'),
    path('get_last_chat/', views.get_last_chat, name='get_last_chat'),
    path('create_post/', views.create_post, name='create_post'),
    path('post_feed/', views.post_feed, name='post_feed'),
    path('add_close_friend/<int:profile_id>/', views.add_close_friend, name='add_close_friend'),
]
