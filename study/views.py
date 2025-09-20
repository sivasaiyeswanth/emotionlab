from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Clip, ParticipantProfile, ClipResponse, ClipQuestion
from .forms import PrePostEmotionForm, PerceivedEmotionForm, SignUpForm
from django.contrib import messages
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

def home(request):
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"User '{user.username}' created successfully. Please log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    profile, _ = ParticipantProfile.objects.get_or_create(user=user)
    profile.ensure_clip_order()
    clip_ids = profile.clip_order
    responses = {r.clip_id: r for r in ClipResponse.objects.filter(participant=user)}
    # Find the next pending clip
    next_idx = None
    for idx, clip_id in enumerate(clip_ids):
        if clip_id not in responses:
            next_idx = idx
            break
    next_clip = Clip.objects.get(id=clip_ids[next_idx]) if next_idx is not None else None
    return render(request, 'study/dashboard.html', {
        'next_clip': next_clip,
        'next_idx': next_idx,
        'profile': profile,
    })

@login_required
def start_session(request, clip_index=0):
    user = request.user
    profile = user.participant_profile
    profile.ensure_clip_order()
    clip_index = int(clip_index)
    if request.method == 'POST':
        form = PrePostEmotionForm(request.POST, context='pre_session')
        if form.is_valid():
            valence = form.cleaned_data.get('question_valence')
            arousal = form.cleaned_data.get('question_arousal')
            profile.pre_session_valence = valence
            profile.pre_session_arousal = arousal
            profile.save(update_fields=['pre_session_valence', 'pre_session_arousal'])
            return redirect('study:play_clip', clip_index=clip_index)
    else:
        form = PrePostEmotionForm(context='pre_session')
    return render(request, 'study/start_session.html', {'form': form, 'profile': profile, 'clip_index': clip_index})

@login_required
def play_clip(request, clip_index):
    user = request.user
    profile = user.participant_profile
    profile.ensure_clip_order()
    clip_ids = profile.clip_order
    clip_index = int(clip_index)
    if clip_index >= len(clip_ids):
        return redirect('study:post_emotion')
    clip = get_object_or_404(Clip, id=clip_ids[clip_index])
    return render(request, 'study/clip_player.html', {
        'clip': clip,
        'clip_index': clip_index,
        'total_clips': len(clip_ids),
    })

@login_required
def clip_questions(request, clip_id):
    user = request.user
    clip = get_object_or_404(Clip, id=clip_id)
    questions = ClipQuestion.objects.filter(context='clip')
    if request.method == 'POST':
        form = PerceivedEmotionForm(request.POST)
        action = request.POST.get('action', 'next')
        if form.is_valid():
            answers = form.cleaned_data
            profile = user.participant_profile
            ClipResponse.objects.update_or_create(
                clip=clip,
                participant=user,
                defaults={
                    'clip_valence': answers.get('question_clipvalence'),
                    'clip_arousal': answers.get('question_cliparousal'),
                    'impact_valence': answers.get('question_impactvalence'),
                    'impact_arousal': answers.get('question_impactarousal'),
                    'participant_valence': profile.pre_session_valence,
                    'participant_arousal': profile.pre_session_arousal,
                }
            )
            clip_ids = profile.clip_order
            next_index = clip_ids.index(clip.id) + 1
            if action == 'exit':
                return redirect('study:dashboard')
            if next_index >= len(clip_ids):
                return redirect('study:post_emotion')
            return redirect('study:play_clip', clip_index=next_index)
        elif action == 'exit':
            # If form invalid but user wants to exit, just go to dashboard
            return redirect('study:dashboard')
    else:
        form = PerceivedEmotionForm()
    return render(request, 'study/clip_questions.html', {
        'clip': clip,
        'form': form,
        'questions': questions,
        'clip_index': clip.order_index,
    })

@login_required
def post_emotion(request):
    user = request.user
    profile = user.participant_profile
    if request.method == 'POST':
        form = PrePostEmotionForm(request.POST, context='post_session')
        if form.is_valid():
            valence = form.cleaned_data.get('question_valence')
            arousal = form.cleaned_data.get('question_arousal')
            profile.post_session_valence = valence
            profile.post_session_arousal = arousal
            profile.save(update_fields=['post_session_valence', 'post_session_arousal'])
            return redirect('study:dashboard')
    else:
        form = PrePostEmotionForm(context='post_session')
    return render(request, 'study/post_emotion.html', {'form': form, 'profile': profile})

