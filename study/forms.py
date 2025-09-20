# study/forms.py
from django import forms
from django.contrib.auth.models import User

from .models import ClipQuestion

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class PrePostEmotionForm(forms.Form):
    """
    Dynamically generates fields for all ClipQuestion objects with context 'pre_session' or 'post_session'.
    """
    def __init__(self, *args, context='pre_session', **kwargs):
        super().__init__(*args, **kwargs)
        questions = ClipQuestion.objects.filter(context=context)
        for q in questions:
            field_name = f"question_{q.code}"
            if q.response_type == 'likert':
                choices = [(str(i), str(i)) for i in range(1, 6)]
                self.fields[field_name] = forms.ChoiceField(
                    label=q.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
            elif q.response_type == 'mcq':
                self.fields[field_name] = forms.ChoiceField(
                    label=q.text,
                    choices=[(c, c) for c in q.choices],
                    required=True
                )
            elif q.response_type == 'free_text':
                self.fields[field_name] = forms.CharField(
                    label=q.text,
                    widget=forms.Textarea,
                    required=False
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=q.text,
                    required=False
                )


class PerceivedEmotionForm(forms.Form):
    """
    Dynamically generates fields for all ClipQuestion objects with context 'clip'.
    """
    def __init__(self, *args, clip=None, **kwargs):
        super().__init__(*args, **kwargs)
        questions = ClipQuestion.objects.filter(context='clip')
        for q in questions:
            field_name = f"question_{q.code}"
            if q.response_type == 'likert':
                choices = [(str(i), str(i)) for i in range(1, 6)]
                self.fields[field_name] = forms.ChoiceField(
                    label=q.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
            elif q.response_type == 'mcq':
                self.fields[field_name] = forms.ChoiceField(
                    label=q.text,
                    choices=[(c, c) for c in q.choices],
                    required=True
                )
            elif q.response_type == 'free_text':
                self.fields[field_name] = forms.CharField(
                    label=q.text,
                    widget=forms.Textarea,
                    required=False
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=q.text,
                    required=False
                )