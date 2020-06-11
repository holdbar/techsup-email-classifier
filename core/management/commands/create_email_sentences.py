import nltk

from django.core.management.base import BaseCommand

from core.models import EmailSentence, Email

class Command(BaseCommand):
    help = 'Creates email sentences from email text'

    def handle(self, *args, **options):
        emails = Email.objects.all()
        for e in emails:
            if not EmailSentence.objects.filter(email=e):
                sentences = nltk.sent_tokenize(e.text)
                for i,s in enumerate(sentences):
                    EmailSentence(
                        text=s,
                        email=e,
                        order=i
                    ).save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created sentences for {emails.count()} emails.'))