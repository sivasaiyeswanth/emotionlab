# study/utils.py
from django.utils import timezone
from .models import DailyProgress

from datetime import date

def get_today_progress(user):
    today = timezone.localdate()
    dp, _ = DailyProgress.objects.get_or_create(participant=user, date=today)
    return dp

def can_start_new_movie(user):
    dp = get_today_progress(user)
    # Allow at most 2 per day
    if dp.movies_completed >= 2:
        return (False, None, 'Daily limit reached. Come back tomorrow.')

    eligible_at = dp.eligible_for_second_movie_at()
    if dp.movies_completed == 1 and timezone.now() < eligible_at:
        return (False, eligible_at, 'Please take a 5-minute break before starting the second movie.')

    return (True, None, None)