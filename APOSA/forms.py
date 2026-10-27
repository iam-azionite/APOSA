from django import forms
from django.contrib.auth.models import User


class CustomUserCreationForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'At least 8 characters'
        }),
        help_text="Password must contain at least 8 characters."
    )

    password2 = forms.CharField(
        label="Confirm Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address'
            }),
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if password and len(password) < 8:
            raise forms.ValidationError(
                "Password must contain at least 8 characters."
            )

        return password

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error(
                'password2',
                "The passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user