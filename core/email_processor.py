import re
import nltk
import pickle
import dateparser
import datetime

from nltk.corpus import wordnet 
from pattern.en import pluralize, singularize, lexeme, tenses
from sklearn.feature_extraction import DictVectorizer
from flair.models import SequenceTagger
from flair.data import Sentence

from core.models import OntologyVariableValue
from core.management.commands.train_classifier import extract_features

class EmailProcessor:
    
    def __init__(self):
        self.crud_verbs = sorted(list(OntologyVariableValue.objects.filter(variable__name='CRUD_VERBS').values_list('text', flat=True)),key=len,reverse=True)
        self.crud_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='CRUD_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.investigation_verbs = sorted(list(OntologyVariableValue.objects.filter(variable__name='INVESTIGATION_VERBS').values_list('text', flat=True)),key=len,reverse=True)
        self.investigation_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='INVESTIGATION_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.urgency_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='URGENCY_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.time_regexp = re.compile(
            r'(?<![\-\:\′\´\’\’\‘\`\'])\b(?P<time>((to|from|untill)\s)?([0-1]?[0-9]|2[0-3])(:|\.|\-)[0-5][0-9])\b(?![\-\:\′\´\’\’\‘\`\']|\.\d)'
        )
        self.date_regexp = re.compile(r'\b(?P<date>(\d{1,4}-\d{1,2}-\d{2,4})|(\d{1,4}\.\d{1,2}\.\d{2,4})|(\d{1,4}\/\d{1,2}\/\d{2,4}))\b')
        self.annotation_regexp = r'\b{}\b(?!<B-|<I-)'
        self.result = {"line": "NEEDS MANUAL CHOICE", "is_urgent": "No"}
        self.tagger = SequenceTagger.load('data/models/taggers/model-var-emb-bert-sampled/final-model.pt')
        self.line_classifier = pickle.load(open('data/models/classifiers/random-forest/line.pickle', 'rb'))
        self.urgency_classifier = pickle.load(open('data/models/classifiers/random-forest/urgency.pickle', 'rb'))

    def get_synonyms(self, word):
        word_synsets = wordnet.synsets(word)
        synonyms = []
        for ws in word_synsets:
            synonyms.extend(list(map(lambda x: x.replace("_"," "), ws.lemma_names())))
        
        return list(set(synonyms))

    def get_time(self, text):
        matches = [m.groupdict().get('time') for m in self.time_regexp.finditer(text) if m.groupdict().get('time')]

        return matches

    def get_date(self, text):
        matches = [m.groupdict().get('date') for m in self.date_regexp.finditer(text) if m.groupdict().get('date')]
        
        return matches

    def get_verb_tense_forms(self, verb):
        all_tense_forms = lexeme(verb)

        return all_tense_forms

    def get_all_word_forms(self, word):
        all_word_forms = [word]
        all_word_forms.append(singularize(word))
        all_word_forms.append(pluralize(word))

        return all_word_forms

    @property
    def get_crud_words_values(self):
        values = []
        for w in self.crud_words:
            values.extend(self.get_all_word_forms(w))

        return sorted(values, key=len, reverse=True)

    @property
    def get_crud_verbs_values(self):
        values = []
        for w in self.crud_verbs:
            values.extend(self.get_verb_tense_forms(w))

        return sorted(values, key=len, reverse=True)

    @property
    def get_investigation_words_values(self):
        values = []
        for w in self.investigation_words:
            values.extend(self.get_all_word_forms(w))

        return sorted(values, key=len, reverse=True)

    @property
    def get_investigation_verbs_values(self):
        values = []
        for w in self.investigation_verbs:
            values.extend(self.get_verb_tense_forms(w))

        return sorted(values, key=len, reverse=True)

    @property
    def get_urgency_words_values(self):
        values = []
        for w in self.urgency_words:
            values.append(w)
            values.extend(self.get_synonyms(w))

        return sorted(values, key=len, reverse=True)


    def annotate_sentence(self, text):
        annotated_text = text
        annotation_map = {
            'DATE': self.get_date(annotated_text),
            'TIME': self.get_time(annotated_text),
            'CRUD_WORDS': self.get_crud_words_values,
            'CRUD_VERBS': self.get_crud_verbs_values,
            'INVESTIGATION_WORDS': self.get_investigation_words_values,
            'INVESTIGATION_VERBS': self.get_investigation_verbs_values,
            'URGENCY_WORDS': self.get_urgency_words_values
        }
        for variable, values in annotation_map.items():
            for w in values:
                r = re.search(self.annotation_regexp.format(w), annotated_text)
                if r:
                    tokens = nltk.word_tokenize(w)
                    annotated_tokens = []
                    for i,t in enumerate(tokens):
                        if i == 0:
                            annotation = f'{t}__B-{variable}'
                            annotated_tokens.append(annotation)
                        else:
                            annotation = f'{t}__I-{variable}'
                            annotated_tokens.append(annotation)
                    annotated_text = re.sub(self.annotation_regexp.format(w), " ".join(annotated_tokens), annotated_text)

        return annotated_text

    def get_model_tagged_sentence(self, text):
        sent_text = ' '.join(nltk.word_tokenize(text))
        sent_obj = Sentence(sent_text)
        self.tagger.predict(sent_obj)

        return sent_obj

    def annotate_email_with_model(self, text):
        annotated_text = ''
        sentences = nltk.sent_tokenize(text)
        for sent in sentences:
            tagged_sentence = self.get_model_tagged_sentence(sent)
            annotated_text += f'{tagged_sentence.to_tagged_string()} '

        return annotated_text

    def get_model_tagged_email_sentences(self, text):
        sentences = nltk.sent_tokenize(text)
        tagged_sentences = []
        for sent in sentences:
            tagged_sentence = self.get_model_tagged_sentence(sent)
            tagged_sentences.append(tagged_sentence)

        return tagged_sentences

    def get_tags_from_email(self, email_sentences):
        tag_dict = {
            'CRUD_WORDS': [],
            'CRUD_VERBS': [],
            'INVESTIGATION_VERBS': [],
            'INVESTIGATION_WORDS': [],
            'URGENCY_WORDS': [],
            'TIME': [],
            'DATE': []
        }
        for es in email_sentences:
            spans = es.get_spans('var')
            for s in spans:
                tag_dict[s.tag].append(s.text)

        return tag_dict

    def check_urgency_with_date(self, date_strings):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        print(today, tomorrow)
        for date_string in date_strings:
            date = dateparser.parse(date_string)
            if date:
                date = date.date()
            print(date == today , date == tomorrow)
            print(date)
            if date == today or date == tomorrow:

                return True
        
        return False

    def check_word(self, word, text, use_synonyms=False):
        words = set()
        if use_synonyms:
            words = set(self.get_synonyms(word))
        words.add(word)
        found_words = []
        for w in words:
            r = re.search(fr'\b{w}\b', text)
            if r:
                found_words.append(word)
        
        return found_words

    def process(self, email):
        found_crud_verbs = []
        for cv in self.crud_verbs:
            found_crud_verbs.extend(self.check_word(cv, email))
        found_crud_words = []
        for cw in self.crud_words:
            found_crud_words.extend(self.check_word(cw, email))
        found_investigation_verbs = []
        for iv in self.investigation_verbs:
            found_investigation_verbs.extend(self.check_word(iv, email))
        found_investigation_words = []
        for iw in self.investigation_words:
            found_investigation_words.extend(self.check_word(iw, email))
        found_urgency_words = []
        for uw in self.urgency_words:
            found_urgency_words.extend(self.check_word(uw, email, True))
        if found_investigation_verbs or found_investigation_words:
            self.result['line'] = "L2"
        if found_crud_verbs and found_crud_words and self.result['line'] != "L2":
            self.result['line'] = "L1"
        self.result['possible_actions'] = found_investigation_verbs + found_crud_verbs
        self.result['possible_objects'] = found_investigation_words + found_crud_words
        if found_urgency_words:
            self.result['is_urgent'] = "Yes"
            self.result['urgency_markers'] = found_urgency_words

    
    def process_with_models(self, email):
        email_sentences = self.get_model_tagged_email_sentences(email)
        features = extract_features(email_sentences)
        tag_dict = self.get_tags_from_email(email_sentences)
        dict_vec = DictVectorizer()
        vectorized_features = dict_vec.fit_transform(features)
        self.result['line'] = self.line_classifier.predict(vectorized_features)[0]
        self.result['is_urgent'] = self.urgency_classifier.predict(vectorized_features)[0]
        self.result['possible_actions'] = tag_dict['INVESTIGATION_VERBS'] + tag_dict['CRUD_VERBS']
        self.result['possible_objects'] = tag_dict['INVESTIGATION_WORDS'] + tag_dict['CRUD_WORDS']
        if tag_dict['TIME']:
            self.result['possible_time'] = tag_dict['TIME']
        if tag_dict['DATE']:
            self.result['possible_date'] = tag_dict['DATE']
        if self.result['is_urgent'] == "No" and tag_dict['DATE']:
            if self.check_urgency_with_date(self.result['possible_date']):
                self.result['is_urgent'] = "Yes"
        if self.result['is_urgent'] == "Yes":
            self.result['urgency_markers'] = tag_dict['URGENCY_WORDS']

    