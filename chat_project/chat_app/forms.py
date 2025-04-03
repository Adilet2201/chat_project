from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Message

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=100)
    profile_pic = forms.ImageField(required=False)
    birthday = forms.DateField(required=False,
                               widget=forms.SelectDateWidget(years=range(1900, 2025)))

    class Meta:
        model = User
        fields = ('username', 'email', 'display_name', 'profile_pic', 'birthday',
                  'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                display_name=self.cleaned_data['display_name'],
                profile_pic=self.cleaned_data.get('profile_pic'),
                birthday=self.cleaned_data.get('birthday'),
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('display_name', 'profile_pic', 'birthday')
