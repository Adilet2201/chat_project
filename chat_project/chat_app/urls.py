from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('profile/', views.update_profile, name='update_profile'),
    path('search/', views.user_search, name='user_search'),
    path('start_chat/<int:profile_id>/', views.start_or_resume_chat, name='start_or_resume_chat'),

]
