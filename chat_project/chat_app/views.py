# chat_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count

# ── Models ────────────────────────────────────────────────────────────────
from .models import Chat, Message, Profile, Post

# ── Forms ─────────────────────────────────────────────────────────────────
from .forms import ProfileForm, PostForm, CustomUserCreationForm, MessageForm

# ── DRF imports ───────────────────────────────────────────────────────────
from rest_framework import viewsets, permissions, serializers
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ChatSerializer,
    MessageSerializer,
    PostSerializer,
)

User = get_user_model()

# ========================================================================
# HTML VIEWS
# ========================================================================

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user, display_name=user.username)
        login(self.request, user)
        return redirect("update_profile")


class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat_list.html"
    context_object_name = "chats"

    def get_queryset(self):
        try:
            profile = self.request.user.profile
            return (
                Chat.objects.filter(participants=profile)
                .annotate(message_count=Count("messages"))
                .order_by("-messages__timestamp")
            )
        except Profile.DoesNotExist:
            return Chat.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            profile = self.request.user.profile
            ctx["current_profile"] = profile
            chatting_with = (
                Chat.objects.filter(participants=profile)
                .values_list("participants__id", flat=True)
            )
            ctx["available_profiles"] = (
                Profile.objects.exclude(id=profile.id)
                .exclude(id__in=chatting_with)
            )
        except Profile.DoesNotExist:
            ctx["current_profile"] = None
            ctx["available_profiles"] = Profile.objects.none()
        return ctx


class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = "chat_detail.html"
    context_object_name = "chat"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chat = self.get_object()
        ctx["messages"] = chat.messages.order_by("timestamp")
        ctx["message_form"] = MessageForm()
        ctx["current_profile"] = getattr(self.request.user, "profile", None)
        self.request.session["last_chat_id"] = chat.pk
        return ctx

    def post(self, request, *args, **kwargs):
        chat = self.get_object()
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return redirect("update_profile")

        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.chat = chat
            msg.sender = profile
            msg.save()
            return redirect("chat_detail", pk=chat.pk)

        ctx = self.get_context_data()
        ctx["message_form"] = form
        return self.render_to_response(ctx)

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        return Chat.objects.filter(participants=profile) if profile else Chat.objects.none()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profile_form.html"
    success_url = reverse_lazy("chat_list")

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist for this user.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserSearchView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "user_search.html"
    context_object_name = "profiles"

    def get_queryset(self):
        q = self.request.GET.get("q")
        if q:
            return (
                Profile.objects.filter(
                    Q(display_name__icontains=q) | Q(user__username__icontains=q)
                )
                .exclude(user=self.request.user)
            )
        return Profile.objects.none()


@login_required
def start_or_resume_chat(request, profile_id):
    current = request.user.profile
    other = get_object_or_404(Profile, pk=profile_id)

    if current == other:
        return redirect("chat_list")

    chat = (
        Chat.objects.annotate(num_participants=Count("participants"))
        .filter(participants=current, num_participants=2)
        .filter(participants=other)
        .first()
    )
    if chat is None:
        chat = Chat.objects.create()
        chat.participants.add(current, other)

    return redirect("chat_detail", pk=chat.pk)


class SetLastChatView(LoginRequiredMixin, View):
    def post(self, request, chat_id):
        try:
            Chat.objects.get(pk=chat_id, participants=request.user.profile)
            request.session["last_chat_id"] = chat_id
            return JsonResponse({"status": "ok"})
        except (Chat.DoesNotExist, Profile.DoesNotExist):
            return JsonResponse(
                {"status": "error", "message": "Chat not found or invalid permissions"},
                status=404,
            )


class GetLastChatView(LoginRequiredMixin, View):
    def get(self, request):
        chat_id = request.session.get("last_chat_id")
        if chat_id:
            try:
                Chat.objects.get(pk=chat_id, participants=request.user.profile)
                return JsonResponse({"last_chat_id": chat_id})
            except (Chat.DoesNotExist, Profile.DoesNotExist):
                del request.session["last_chat_id"]
        return JsonResponse({"last_chat_id": None})


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "create_post.html"
    success_url = reverse_lazy("post_feed")

    def form_valid(self, form):
        try:
            form.instance.owner = self.request.user.profile
            return super().form_valid(form)
        except Profile.DoesNotExist:
            form.add_error(None, "You need a profile to create posts.")
            return self.form_invalid(form)


class PostFeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "post_feed.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        try:
            profile = self.request.user.profile
            friend_of_ids = profile.close_friend_of.values_list("id", flat=True)
            return (
                Post.objects.filter(
                    Q(privacy="public")
                    | Q(owner=profile)
                    | (Q(owner_id__in=friend_of_ids) & Q(privacy="close"))
                )
                .distinct()
                .order_by("-created_at")
            )
        except Profile.DoesNotExist:
            return Post.objects.filter(privacy="public").order_by("-created_at")


@login_required
def add_close_friend(request, profile_id):
    try:
        current = request.user.profile
        friend = get_object_or_404(Profile, pk=profile_id)
        if current != friend:
            current.close_friends.add(friend)
    except Profile.DoesNotExist:
        pass
    return redirect(request.META.get("HTTP_REFERER", "chat_list"))

# ========================================================================
# API VIEWSETS
# ========================================================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.get_object().user == self.request.user:
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not have permission to edit this profile.")

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied

        raise PermissionDenied("Profile creation should be linked to user registration.")


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        return Chat.objects.filter(participants=profile) if profile else Chat.objects.none()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        if profile:
            chat_ids = Chat.objects.filter(participants=profile).values_list("id", flat=True)
            return Message.objects.filter(chat_id__in=chat_ids).order_by("-timestamp")
        return Message.objects.none()

    def perform_create(self, serializer):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise serializers.ValidationError("User profile not found.")

        chat = serializer.validated_data.get("chat")
        if not Chat.objects.filter(pk=chat.id, participants=profile).exists():
            raise serializers.ValidationError("You are not a participant of this chat.")

        serializer.save(sender=profile)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            profile = self.request.user.profile
            friend_of_ids = profile.close_friend_of.values_list("id", flat=True)
            return (
                Post.objects.filter(
                    Q(privacy="public")
                    | Q(owner=profile)
                    | (Q(owner_id__in=friend_of_ids) & Q(privacy="close"))
                )
                .distinct()
                .order_by("-created_at")
            )
        except Profile.DoesNotExist:
            return Post.objects.filter(privacy="public").order_by("-created_at")

    def perform_create(self, serializer):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise serializers.ValidationError("User profile not found.")
        serializer.save(owner=profile)
