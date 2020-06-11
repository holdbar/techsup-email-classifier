import nltk

from django.core.management.base import BaseCommand

from core.models import EmailSentence
from core.email_processor import EmailProcessor

class Command(BaseCommand):
    help = 'Annotates email sentences.'

    def handle(self, *args, **options):
        ep = EmailProcessor()
        sentences = EmailSentence.objects.all()
        for s in sentences:
            annotated_text = ep.annotate_sentence(s.text)
            s.annotated_text = annotated_text
            s.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully annotated {sentences.count()} sentences.'))