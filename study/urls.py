# study/urls.py (app)
from django.urls import path
from . import views

app_name = 'study'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start_session/<int:clip_index>/', views.start_session, name='start_session'),
    path('clip/<int:clip_index>/', views.play_clip, name='play_clip'),
    path('clip_questions/<int:clip_id>/', views.clip_questions, name='clip_questions'),
    path('post/', views.post_emotion, name='post_emotion'),
    path('accounts/signup/', views.signup, name='signup'),
]