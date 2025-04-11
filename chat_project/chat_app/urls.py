# chat_app/urls.py
from django.urls import path, include
from rest_framework import routers

from . import views
from .views import (
    UserViewSet,
    ProfileViewSet,
    ChatViewSet,
    MessageViewSet,
    PostViewSet,
)

# ─────────────────────────────────────────────────────────────
# API router
# ─────────────────────────────────────────────────────────────
router = routers.DefaultRouter()
router.register(r'users',     UserViewSet,     basename='user')
router.register(r'profiles',  ProfileViewSet,  basename='profile')
router.register(r'chats',     ChatViewSet,     basename='chat')
router.register(r'messages',  MessageViewSet,  basename='message')
router.register(r'posts',     PostViewSet,     basename='post')

# ─────────────────────────────────────────────────────────────
# Web & API URL patterns
# ─────────────────────────────────────────────────────────────
urlpatterns = [
    # HTML views
    path('register/',                       views.RegisterView.as_view(),       name='register'),
    path('',                                views.ChatListView.as_view(),       name='chat_list'),
    path('chat/<int:pk>/',                  views.ChatDetailView.as_view(),     name='chat_detail'),
    path('profile/',                        views.ProfileUpdateView.as_view(),  name='update_profile'),
    path('search/',                         views.UserSearchView.as_view(),     name='user_search'),
    path('start_chat/<int:profile_id>/',    views.start_or_resume_chat,         name='start_or_resume_chat'),
    path('set_last_chat/<int:chat_id>/',    views.SetLastChatView.as_view(),    name='set_last_chat'),
    path('get_last_chat/',                  views.GetLastChatView.as_view(),    name='get_last_chat'),
    path('create_post/',                    views.CreatePostView.as_view(),     name='create_post'),
    path('post_feed/',                      views.PostFeedView.as_view(),       name='post_feed'),
    path('add_close_friend/<int:profile_id>/', views.add_close_friend,         name='add_close_friend'),

    # API
    path('api/',       include(router.urls)),
    path('api-auth/',  include('rest_framework.urls', namespace='rest_framework')),
]
