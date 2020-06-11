import nltk

from django.core.management.base import BaseCommand

from core.models import EmailSentence

class Command(BaseCommand):
    help = 'Save annotated sentences as sequence labeling dataset.'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', help='File name to store sequence labeling dataset.')

    def handle(self, *args, **options):
        file = options.get('file') or 'annotated_sentences'
        with open(f'data/txt/{file}.txt', 'w') as f:
            sentences = EmailSentence.objects.all()
            count = len(sentences)
            for i, s in enumerate(sentences): 
                text = s.annotated_text 
                tokens = nltk.word_tokenize(text) 
                for t in tokens: 
                    if '__B-' in t or '__I-' in t: 
                        word, label = t.split('__') 
                        line = f'{word} {label.strip()}\n' 
                    else: 
                        line = f'{t} O\n' 
                    f.write(line)
                if i != count - 1:
                    f.write('\n')

        
        self.stdout.write(self.style.SUCCESS(f'Successfully saved {count} sentences to dataset file.'))