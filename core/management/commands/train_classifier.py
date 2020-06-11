import pickle
import nltk

from collections import defaultdict

from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

from flair.data import Sentence
from flair.models import SequenceTagger

from django.core.management.base import BaseCommand

from core.models import Email, EmailSentence

def extract_features(email_sentences):
    features = dict()
    annotations = defaultdict(list)
    for s in email_sentences:
        for span in s.get_spans('var'):
            annotations[span.tag].append(span.text)
    
    features['cw'] = 1 if len(annotations.get('CRUD_WORDS',[])) > 0 else 0
    features['cv'] = 1 if len(annotations.get('CRUD_VERBS',[])) > 0 else 0 
    features['iw'] = 1 if len(annotations.get('INVESTIGATION_WORDS',[])) > 0 else 0
    features['iv'] = 1 if len(annotations.get('INVESTIGATION_VERBS',[])) > 0 else 0
    features['uw'] = 1 if len(annotations.get('URGENCY_WORDS',[])) > 0 else 0

    return features
        

def get_labels_from_features(features):
    line, urgency = 'NEEDS_MANUAL_CHOICE', 'No'
    if features['iw'] or features['iv']:
        line = 'L2'
    elif features['cw'] and features['cv'] and line != 'L2':
        line = 'L1'
    if features['uw']:
        urgency = 'Yes'

    return line, urgency

class Command(BaseCommand):
    help = 'Annotates email sentences.'

    def add_arguments(self, parser):
        parser.add_argument('-mf', '--model_folder', help='Name of sequence labeling model folder.')
        parser.add_argument('-cf', '--classifier_folder', help='Name of classifier folder.')

    def handle(self, *args, **options):
        model_folder = options.get('model_folder') or 'model-var-emb-bert-sampled'
        classifier_folder = options.get('classifier_folder') or 'random-forest'
        model = SequenceTagger.load(f'data/models/taggers/{model_folder}/final-model.pt')

        emails = Email.objects.all()
        labels_data = []
        features_data = []
        for email in emails:
            print(email)
            sentences = EmailSentence.objects.filter(email=email).order_by('order')
            email_sentences = []
            for s in sentences:
                sentence = Sentence(s.text)
                model.predict(sentence)
                email_sentences.append(sentence)
            features = extract_features(email_sentences)
            labels = get_labels_from_features(features)
            labels_data.append(labels)
            features_data.append(features)

        X_train, X_test, y_train, y_test = train_test_split(features_data, labels_data, test_size=0.33, random_state=42)
        clf_line = RandomForestClassifier(max_depth=2, random_state=0)
        dict_vec = DictVectorizer()
        vectorized_features = dict_vec.fit_transform(X_train)
        clf_line.fit(vectorized_features, [y[0] for y in y_train])
        print(classification_report([y[0] for y in y_test], clf_line.predict(dict_vec.fit_transform(X_test))))

        pickle.dump(clf_line, open(f'data/models/classifiers/{classifier_folder}/line.pickle', 'wb'))

        clf_urgency = RandomForestClassifier(max_depth=2, random_state=0)
        dict_vec = DictVectorizer()
        vectorized_features = dict_vec.fit_transform(X_train)
        clf_urgency.fit(vectorized_features, [y[1] for y in y_train])
        print(classification_report([y[1] for y in y_test], clf_urgency.predict(dict_vec.fit_transform(X_test))))

        pickle.dump(clf_urgency, open(f'data/models/classifiers/{classifier_folder}/urgency.pickle', 'wb'))
        
        
        self.stdout.write(self.style.SUCCESS(f'Successfully trained classifiers.'))
