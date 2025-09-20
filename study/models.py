from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Clip(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='clips/')  # Put your media under MEDIA_ROOT/clips
    order_index = models.PositiveIntegerField()  # for admin sorting only

    class Meta:
        ordering = ['order_index', 'title']

    def __str__(self):
        return f"{self.order_index:02d} — {self.title}"

class ParticipantProfile(models.Model):
    def ensure_clip_order(self):
        """Generate a randomized clip order for this user if not already set."""
        if not self.clip_order:
            clip_ids = list(Clip.objects.values_list('id', flat=True))
            import random
            random.shuffle(clip_ids)
            self.clip_order = clip_ids
            self.save(update_fields=['clip_order'])
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant_profile')
    # Per-user randomized clip order (list of Clip IDs)
    clip_order = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    # Valence/arousal before and after session
    pre_session_valence = models.FloatField(null=True, blank=True)
    pre_session_arousal = models.FloatField(null=True, blank=True)
    post_session_valence = models.FloatField(null=True, blank=True)
    post_session_arousal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user})"

class ClipQuestion(models.Model):
    code = models.CharField(max_length=64, unique=True)
    text = models.CharField(max_length=500)
    response_type = models.CharField(max_length=32, default='likert')  # 'likert', 'mcq', 'free_text'
    choices = models.JSONField(default=list, blank=True)  # for mcq or labeled scales
    QUESTION_CONTEXTS = [
        ('clip', 'After Clip'),
        ('pre_session', 'Before Session'),
        ('post_session', 'After Session'),
    ]
    context = models.CharField(max_length=16, choices=QUESTION_CONTEXTS, default='clip', help_text='When to ask this question')

    def __str__(self):
        return f"{self.code} ({self.get_context_display()})"

class ClipResponse(models.Model):
    clip = models.ForeignKey(Clip, on_delete=models.PROTECT)
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clip_responses')
    # After-clip data
    clip_valence = models.IntegerField(null=True, blank=True, help_text='How pleasant does the clip seem to be?')
    clip_arousal = models.IntegerField(null=True, blank=True, help_text='How active or energetic does the clip seem to be?')
    impact_valence = models.IntegerField(null=True, blank=True, help_text='How pleasant are you feeling after watching the clip?')
    impact_arousal = models.IntegerField(null=True, blank=True, help_text='How active/energetic are you feeling after watching the clip?')
    participant_valence = models.IntegerField(null=True, blank=True, help_text='Participant valence before session')
    participant_arousal = models.IntegerField(null=True, blank=True, help_text='Participant arousal before session')
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('clip', 'participant'),)
        ordering = ['clip__order_index']

    def __str__(self):
        return f"Response({self.participant}, {self.clip})"
