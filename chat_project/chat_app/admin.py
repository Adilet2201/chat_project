from django.contrib import admin
from .models import Profile, Chat, Message

@admin.action(description='Block selected users')
def block_users(modeladmin, request, queryset):
    queryset.update(is_blocked=True)

@admin.action(description='Unblock selected users')
def unblock_users(modeladmin, request, queryset):
    queryset.update(is_blocked=False)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'birthday', 'is_blocked')
    actions = [block_users, unblock_users]

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Chat)
admin.site.register(Message)
