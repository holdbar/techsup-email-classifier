import nltk

from django.core.management.base import BaseCommand

from flair.datasets import ColumnCorpus
from flair.embeddings import (
    TokenEmbeddings, 
    WordEmbeddings, 
    StackedEmbeddings, 
    FlairEmbeddings,
    TransformerWordEmbeddings
)
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

class Command(BaseCommand):
    help = 'Train model on sequence labeling dataset.'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', help='File name of sequence labeling dataset.')
        parser.add_argument('-mf', '--model_folder', help='Name of sequence labeling model folder.')

    def handle(self, *args, **options):
        file = options.get('file') or 'annotated_sentences'
        model_folder = options.get('model_folder') or 'model-var'
        columns = {0: 'text', 1: 'var'}
        data_folder = 'data/txt'

        corpus = ColumnCorpus(data_folder, columns,
                              train_file=f'{file}.txt')
        
        tag_type = 'var'

        tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)

        embedding_types = [
            WordEmbeddings('glove'),

            # comment in this line to use character embeddings
            # CharacterEmbeddings(),

            # comment in these lines to use flair embeddings
            # FlairEmbeddings('news-forward'),
            # FlairEmbeddings('news-backward'),
            TransformerWordEmbeddings('bert-base-uncased'),
        ]

        embeddings = StackedEmbeddings(embeddings=embedding_types)

        tagger = SequenceTagger(hidden_size=256,
                                embeddings=embeddings,
                                tag_dictionary=tag_dictionary,
                                tag_type=tag_type,
                                use_crf=True)

        trainer = ModelTrainer(tagger, corpus)

        trainer.train(f'data/models/taggers/{model_folder}',
                    learning_rate=0.1,
                    mini_batch_size=32,
                    max_epochs=150)

        
        self.stdout.write(self.style.SUCCESS(f'Successfully trained model on dataset file.'))