from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, ProfileUpdateForm
from .models import Chat, Message, Profile
from django.http import HttpResponse

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