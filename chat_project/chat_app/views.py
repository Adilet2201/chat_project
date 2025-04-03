from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q

from django.contrib.auth.models import User
from .forms import RegistrationForm, ProfileUpdateForm
from .models import Chat, Message, Profile, Post

# --- Пример CBV для регистрации --- #
class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('chat_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Логиним пользователя сразу
        login(self.request, self.object)
        return response

# --- Пример CBV для списка чатов --- #
class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'chat_list.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return self.request.user.profile.chats.all()

# --- Пример CBV для детального просмотра чата (со способностью принимать POST) --- #
class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'chat_detail.html'
    context_object_name = 'chat'

    def get_queryset(self):
        # показываем только чаты, в которых участвует текущий пользователь
        return Chat.objects.filter(participants=self.request.user.profile)

    def post(self, request, *args, **kwargs):
        """Обработка отправки сообщений."""
        self.object = self.get_object()  # получаем чат
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        if content or image:
            Message.objects.create(
                chat=self.object,
                sender=request.user.profile,
                content=content,
                image=image
            )
        return redirect('chat_detail', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all().order_by('timestamp')
        return context

# --- Профиль (UpdateView) --- #
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile_form.html'
    success_url = reverse_lazy('chat_list')

    def get_object(self, queryset=None):
        return self.request.user.profile

# --- Поиск пользователей (CBV) --- #
class UserSearchView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'user_search.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Profile.objects.filter(display_name__icontains=query).exclude(user=self.request.user)
        return Profile.objects.none()

# --- Пример создания/просмотра постов --- #
class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content', 'image', 'privacy']  # минимальный набор, или сделайте форму
    template_name = 'create_post.html'
    success_url = reverse_lazy('post_feed')

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

class PostFeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # public posts
        public_posts = Post.objects.filter(privacy='public')
        # close friend posts (если текущий user в close_friends автора или сам автор)
        close_posts = Post.objects.filter(
            privacy='close'
        ).filter(
            Q(owner__close_friends=self.request.user.profile) | Q(owner=self.request.user.profile)
        )
        return (public_posts | close_posts).order_by('-created_at')

# --- Работа с сессией. Можно объединить в один View или сделать два ---
class SetLastChatView(LoginRequiredMixin, View):
    def get(self, request, chat_id):
        request.session['last_chat_id'] = chat_id
        return HttpResponse(f"Last chat set to {chat_id}")

    # Или метод post, если хотите
    def post(self, request, chat_id):
        request.session['last_chat_id'] = chat_id
        return HttpResponse(f"Last chat set to {chat_id}")

class GetLastChatView(LoginRequiredMixin, View):
    def get(self, request):
        last_chat = request.session.get('last_chat_id', None)
        return HttpResponse(f"Last visited chat id is {last_chat}")


# --- Функция для старта чата (можно переписать на CBV) ---
@login_required
def start_or_resume_chat(request, profile_id):
    target_profile = get_object_or_404(Profile, id=profile_id)
    my_profile = request.user.profile
    # Проверяем, есть ли уже чат
    chat = Chat.objects.filter(participants=my_profile).filter(participants=target_profile).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(my_profile, target_profile)
    return redirect('chat_detail', pk=chat.id)

# --- Добавить close_friend ---
@login_required
def add_close_friend(request, profile_id):
    friend = get_object_or_404(Profile, id=profile_id)
    request.user.profile.close_friends.add(friend)
    return redirect('user_search')
