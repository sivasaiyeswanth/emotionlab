from django.core.management.base import BaseCommand
from study.models import ClipResponse
import pandas as pd

class Command(BaseCommand):
    help = 'Export all ClipResponse objects to an Excel file.'

    def handle(self, *args, **options):
        responses = ClipResponse.objects.select_related('clip', 'participant')
        data = []
        def make_naive(dt):
            if dt is not None and hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt

        for r in responses:
            data.append({
                'participant': r.participant.username,
                'clip_order': r.clip.order_index if r.clip else '',
                'clip_title': r.clip.title if r.clip else '',
                'clip_valence': r.clip_valence,
                'clip_arousal': r.clip_arousal,
                'impact_valence': r.impact_valence,
                'impact_arousal': r.impact_arousal,
                'participant_valence': r.participant_valence,
                'participant_arousal': r.participant_arousal,
                'created_at': make_naive(r.created_at),
            })
        df = pd.DataFrame(data)
        output_path = 'clip_responses_export.xlsx'
        df.to_excel(output_path, index=False)
        self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} clip responses to {output_path}'))
