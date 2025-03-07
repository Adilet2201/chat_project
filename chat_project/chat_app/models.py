from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name

class Chat(models.Model):
    participants = models.ManyToManyField(Profile, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        names = ", ".join([p.display_name for p in self.participants.all()])
        return f"Chat between {names}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.display_name} at {self.timestamp}"
