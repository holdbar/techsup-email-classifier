import re
import nltk
from nltk.corpus import wordnet 

from core.models import OntologyVariableValue

class EmailProcessor:
    
    def __init__(self):
        self.crud_verbs = sorted(list(OntologyVariableValue.objects.filter(variable__name='CRUD_VERBS').values_list('text', flat=True)),key=len,reverse=True)
        self.crud_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='CRUD_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.investigation_verbs = sorted(list(OntologyVariableValue.objects.filter(variable__name='INVESTIGATION_VERBS').values_list('text', flat=True)),key=len,reverse=True)
        self.investigation_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='INVESTIGATION_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.urgency_words = sorted(list(OntologyVariableValue.objects.filter(variable__name='URGENCY_WORDS').values_list('text', flat=True)),key=len,reverse=True)
        self.result = {"line": "NEEDS MANUAL CHOICE", "is_urgent": "No"}

    def get_synonyms(self, word):
        word_synsets = wordnet.synsets(word)
        synonyms = []
        for ws in word_synsets:
            synonyms.extend(list(map(lambda x: x.replace("_"," "), ws.lemma_names())))
        
        return set(synonyms)

    def check_word(self, word, text, use_synonyms=False):
        words = set()
        if use_synonyms:
            words = self.get_synonyms(word)
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

    

    