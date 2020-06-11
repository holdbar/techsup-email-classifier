import re
import random

import nltk

from django.core.management.base import BaseCommand

from core.models import Email, Source
from core.email_processor import EmailProcessor

def get_random_date():
    separator = random.choice(['.','/','-'])
    year = random.choice(['17','18','19','20','2017','2018','2019','2020'])
    month = random.choice(['01','02','03','04','05','06','07','08','09','10','11','12'])
    day = random.choice([
        '01','02','03','04','05','06','07','08','09','10','11','12',
        '13','14','15','16','17','18','19','20','21','22','23','24',
        '25','26','27','28','29','30','31'
    ])

    return f'{day}{separator}{month}{separator}{year}'

def get_random_time():
    separator = random.choice(['.',':','-'])
    hours = random.choice(['09','10','11','12','13','14','15','16','17','18'])
    minutes = random.choice(['00','10','15','20','30','45', '50'])

    return f'{hours}{separator}{minutes}'

def get_upsampled_emails(text, email_processor):
    samples = []
    sample_text = text
    times = email_processor.get_time(text)
    dates = email_processor.get_date(text)
    urgencies = [
        w for w in email_processor.get_urgency_words_values if email_processor.check_word(w, text)
    ]
    if dates:
        for d in dates:
            for i in range(5):
                samples.append(re.sub(fr'\b{d}\b', get_random_date(), sample_text))
    elif times:
        for t in times:
            for i in range(5):
                samples.append(re.sub(fr'\b{t}\b', get_random_time(), sample_text))
        
    if urgencies:
        for u in urgencies:
            synonyms = email_processor.get_synonyms(u)
            for s in synonyms:
                samples.append(re.sub(fr'\b{u}\b', s, sample_text))
    elif sample_text != text:
        samples.append(sample_text)

    return samples

class Command(BaseCommand):
    help = 'Augments email sentences with data time and urgency words.'

    def handle(self, *args, **options):
        ep = EmailProcessor()
        source = Source.objects.get(pk=1) # uk/ru dataset
        new_source = Source.objects.get(pk=2) # uk/ru dataset
        emails = Email.objects.filter(source=source) 
        for e in emails:
            samples = get_upsampled_emails(e.text,ep)
            if samples:
                for s in samples:
                    Email(
                        text=s,
                        source=new_source,
                        manual_annotation_info=e.manual_annotation_info
                    ).save()

        self.stdout.write(self.style.SUCCESS(f'Successfully augmented emails.'))