from django.contrib import admin
from .models import Profile, Chat, Message, Post

@admin.action(description='Block selected users')
def block_users(modeladmin, request, queryset):
    queryset.update(is_blocked=True)

@admin.action(description='Unblock selected users')
def unblock_users(modeladmin, request, queryset):
    queryset.update(is_blocked=False)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'birthday', 'is_blocked')
    list_filter = ('is_blocked',)
    search_fields = ('display_name', 'user__username')
    actions = [block_users, unblock_users]

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'timestamp')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'privacy', 'created_at')
    list_filter = ('privacy',)
    search_fields = ('owner__display_name', 'content')
