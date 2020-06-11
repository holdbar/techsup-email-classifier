# Training metrics

### First try before augmentation
```
2020-05-29 16:29:47,925 Testing using best model ...
2020-05-29 16:29:47,925 loading file data/models/taggers/model-var/best-model.pt
2020-05-29 16:29:49,013 0.8590	0.7614	0.8072
2020-05-29 16:29:49,013 
MICRO_AVG: acc 0.8072 - f1-score 0.8072
MACRO_AVG: acc 0.6101 - f1-score 0.6101
CRUD_VERBS tp: 21 - fp: 4 - fn: 6 - tn: 21 - precision: 0.8400 - recall: 0.7778 - accuracy: 0.8077 - f1-score: 0.8077
CRUD_WORDS tp: 41 - fp: 5 - fn: 5 - tn: 41 - precision: 0.8913 - recall: 0.8913 - accuracy: 0.8913 - f1-score: 0.8913
DATE       tp: 0 - fp: 0 - fn: 5 - tn: 0 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
INVESTIGATION_VERBS tp: 1 - fp: 0 - fn: 0 - tn: 1 - precision: 1.0000 - recall: 1.0000 - accuracy: 1.0000 - f1-score: 1.0000
INVESTIGATION_WORDS tp: 2 - fp: 2 - fn: 1 - tn: 2 - precision: 0.5000 - recall: 0.6667 - accuracy: 0.5714 - f1-score: 0.5714
TIME       tp: 2 - fp: 0 - fn: 0 - tn: 2 - precision: 1.0000 - recall: 1.0000 - accuracy: 1.0000 - f1-score: 1.0000
URGENCY_WORDS tp: 0 - fp: 0 - fn: 4 - tn: 0 - precision: 0.0000 - recall: 0.0000 - accuracy: 0.0000 - f1-score: 0.0000
```
### With augmentation
```
2020-06-03 20:58:16,176 Testing using best model ...
2020-06-03 20:58:16,177 loading file data/models/taggers/model-var-emb-bert-sampled/best-model.pt
2020-06-03 20:58:55,197 0.9664	0.9753	0.9708
2020-06-03 20:58:55,197 
MICRO_AVG: acc 0.9708 - f1-score 0.9708
MACRO_AVG: acc 0.9575 - f1-score 0.9575
CRUD_VERBS tp: 65 - fp: 1 - fn: 2 - tn: 65 - precision: 0.9848 - recall: 0.9701 - accuracy: 0.9774 - f1-score: 0.9774
CRUD_WORDS tp: 155 - fp: 3 - fn: 4 - tn: 155 - precision: 0.9810 - recall: 0.9748 - accuracy: 0.9779 - f1-score: 0.9779
DATE       tp: 13 - fp: 1 - fn: 0 - tn: 13 - precision: 0.9286 - recall: 1.0000 - accuracy: 0.9630 - f1-score: 0.9630
INVESTIGATION_VERBS tp: 12 - fp: 2 - fn: 1 - tn: 12 - precision: 0.8571 - recall: 0.9231 - accuracy: 0.8889 - f1-score: 0.8889
INVESTIGATION_WORDS tp: 29 - fp: 4 - fn: 0 - tn: 29 - precision: 0.8788 - recall: 1.0000 - accuracy: 0.9355 - f1-score: 0.9355
TIME       tp: 12 - fp: 0 - fn: 1 - tn: 12 - precision: 1.0000 - recall: 0.9231 - accuracy: 0.9600 - f1-score: 0.9600
URGENCY_WORDS tp: 30 - fp: 0 - fn: 0 - tn: 30 - precision: 1.0000 - recall: 1.0000 - accuracy: 1.0000 - f1-score: 1.0000
2020-06-03 20:58:55,197 ----------------------------------------------------------------------------------------------------
```
#### Line
                     precision    recall  f1-score   support

                 L1       0.99      1.00      0.99        92
                 L2       0.95      1.00      0.97        55
    NEEDS_MANUAL_CHOICE       0.00      0.00      0.00         4

           accuracy                           0.97       151
          macro avg       0.65      0.67      0.66       151
       weighted avg       0.95      0.97      0.96       151


#### Urgency
              precision    recall  f1-score   support

          No       1.00      1.00      1.00       105
         Yes       1.00      1.00      1.00        46

    accuracy                           1.00       151
   macro avg       1.00      1.00      1.00       151
weighted avg       1.00      1.00      1.00       151


# Result accuracy metrics
Total emails = 167
#### Baseline

##### Line
- Incorrect = 47
- Correct = 120
- Accuracy = 0,71
- Needs Manual Choice = 9

#### Model

##### Line
- Incorrect = 23 
- Correct = 154 
- Accuracy = 0,92
- Needs Manual Choice = 0

##### Urgency
- Incorrect = 21
- Correct = 156
- Accuracy = 0,93

