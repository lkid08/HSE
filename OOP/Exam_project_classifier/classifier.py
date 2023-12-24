from transformers import pipeline
from config import *


class Classifier:
    def __init__(self):
        self.classifier = pipeline(TASK, model=MODEL)
        self.candidate_labels = CANDIDATE_LABELS
        

    def get_candidate_labels(self):
        for label in self.candidate_labels:
            print(f'- {label}')
        print(len(self.candidate_labels) + ' шт.')

    def add_candidate_label(self, label):
        self.candidate_labels.append(label)

    def remove_candidate_label(self, label):
        if label in self.candidate_labels:
            self.candidate_labels.remove(label)


    def classify_text(self, text):

        classified = self.classifier(text, self.candidate_labels, multi_label=False)

        mapped = [(classified['labels'][i], classified['scores'][i]) for i, label in enumerate(classified['labels'])]

        return mapped
    

# class ArticleClassifier(Classifier):

#     # stuff specific to articles? 


# class ToxicClassifier(Classifier):

#     # only toxicity classifier?

