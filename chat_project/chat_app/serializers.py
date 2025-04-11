# chat_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Chat, Message, Post

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model (optional, but useful for Profile)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # Add other fields as needed

class ProfileSerializer(serializers.ModelSerializer):
    # Makes the user field read-only and shows nested user details
    user = UserSerializer(read_only=True)
    # Shows display names for close friends instead of just IDs
    close_friends = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'display_name',
            'profile_pic',
            'birthday',
            'is_blocked',
            'close_friends'
        ]
        # Make user field settable indirectly if needed, or handle in view/profile creation logic
        # read_only_fields = ['user']

class MessageSerializer(serializers.ModelSerializer):
    # Show sender's display name instead of Profile ID
    sender = serializers.StringRelatedField(read_only=True)
    # Make chat field writeable by ID but readable with more info if needed
    # chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all()) # Example if you want to assign by ID

    class Meta:
        model = Message
        fields = [
            'id',
            'chat',
            'sender',
            'content',
            'image',
            'timestamp'
         ]
        read_only_fields = ['timestamp', 'sender'] # Typically set by the system/logged-in user

class ChatSerializer(serializers.ModelSerializer):
    # Show participants' display names
    participants = ProfileSerializer(many=True, read_only=True) # Or StringRelatedField for just names
    # Optionally include related messages (can be nested or linked)
    # messages = MessageSerializer(many=True, read_only=True) # Careful: Can be large!

    class Meta:
        model = Chat
        fields = [
            'id',
            'participants',
            'created_at',
            # 'messages' # Add if you want nested messages
        ]
        read_only_fields = ['created_at']

class PostSerializer(serializers.ModelSerializer):
    # Show owner's display name
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'owner',
            'content',
            'image',
            'privacy',
            'created_at'
        ]
        read_only_fields = ['created_at', 'owner'] # Owner usually set based on logged-in user