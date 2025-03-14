# Generated by Django 4.2.5 on 2025-03-14 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='close_friends',
            field=models.ManyToManyField(blank=True, related_name='close_friend_of', to='chat_app.profile'),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='post_images/')),
                ('privacy', models.CharField(choices=[('public', 'Public'), ('close', 'Close Friends')], default='public', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='chat_app.profile')),
            ],
        ),
    ]
