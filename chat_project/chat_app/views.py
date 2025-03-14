from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, ProfileUpdateForm
from .models import Chat, Message, Profile,Post
from django.http import HttpResponse
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_list')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def chat_list(request):
    profile = request.user.profile
    chats = profile.chats.all()
    return render(request, 'chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user.profile not in chat.participants.all():
        return HttpResponse("You are not a participant of this chat.", status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        if content or image:
            Message.objects.create(chat=chat, sender=request.user.profile, content=content, image=image)
    messages = chat.messages.all().order_by('timestamp')
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('chat_list')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile_form.html', {'form': form})


@login_required
def user_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        # Search in the display_name field (you can extend to search by username or email)
        results = Profile.objects.filter(display_name__icontains=query).exclude(user=request.user)
    return render(request, 'user_search.html', {'profiles': results, 'query': query})

@login_required
def start_or_resume_chat(request, profile_id):
    target_profile = get_object_or_404(Profile, id=profile_id)
    my_profile = request.user.profile

    # Check if a chat exists that includes both the current user and the target user.
    chat = Chat.objects.filter(participants=my_profile).filter(participants=target_profile).first()
    if not chat:
        # If no chat exists, create a new one
        chat = Chat.objects.create()
        chat.participants.add(my_profile, target_profile)
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def set_last_chat(request, chat_id):
    # Store the last visited chat id in session
    request.session['last_chat_id'] = chat_id
    return HttpResponse(f"Last chat set to {chat_id}")

@login_required
def get_last_chat(request):
    last_chat = request.session.get('last_chat_id', None)
    return HttpResponse(f"Last visited chat id is {last_chat}")

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        privacy = request.POST.get('privacy', 'public')
        image = request.FILES.get('image')
        if content or image:
            Post.objects.create(
                owner=request.user.profile,
                content=content,
                image=image,
                privacy=privacy
            )
            return redirect('post_feed')
    return render(request, 'create_post.html')

@login_required
def post_feed(request):
    # Public posts: visible to everyone.
    public_posts = Post.objects.filter(privacy='public')
    
    # Close friends posts: visible if the current user is in the owner's close_friends list or if the current user is the owner.
    close_posts = Post.objects.filter(
        privacy='close'
    ).filter(
        Q(owner__close_friends=request.user.profile) | Q(owner=request.user.profile)
    )
    
    # Combine the querysets and order by newest first.
    posts = (public_posts | close_posts).order_by('-created_at')
    return render(request, 'post_feed.html', {'posts': posts})

@login_required
def add_close_friend(request, profile_id):
    friend = get_object_or_404(Profile, id=profile_id)
    request.user.profile.close_friends.add(friend)
    return redirect('user_search')