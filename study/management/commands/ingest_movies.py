# study/management/commands/ingest_movies.py

from django.core.management.base import BaseCommand
from study.models import Clip
from pathlib import Path

class Command(BaseCommand):
    help = 'Scan media/clips/ and add all clips to the Clip model, ignoring movies.'

    def add_arguments(self, parser):
        parser.add_argument('--root', default='media/clips', help='Path to root folder containing movie subfolders')

    def handle(self, *args, **opts):
        root = Path(opts['root']).expanduser().resolve()
        assert root.exists(), f"Root not found: {root}"

        # Gather all clips from all movie folders
        all_clips = []
        for mdir in root.iterdir():
            if mdir.is_dir():
                for f in mdir.iterdir():
                    if f.is_file():
                        all_clips.append((mdir.name, f))

        # Sort all clips lexicographically by movie name then filename
        all_clips.sort(key=lambda x: (x[0], x[1].name))

        # Clear all existing clips
        Clip.objects.all().delete()

        for idx, (movie_name, f) in enumerate(all_clips):
            Clip.objects.create(
                title=f.name,
                order_index=idx,
                file=f"clips/{movie_name}/{f.name}"
            )
            self.stdout.write(self.style.SUCCESS(f"Added clip {idx}: {movie_name}/{f.name}"))

        self.stdout.write(self.style.SUCCESS('Ingestion complete.'))