from __future__ import division
from collections import Counter, defaultdict
from sklearn.model_selection import train_test_split
from konlpy.tag import Twitter
import pandas as pd
import math
import random
import re
import glob


def tokenize(message):
    '''문장을 단어 단위로 잘라주는 함수
    message : 단어 단위로 자를 문장

    return  : 중복을 제거한 단어들
    '''
    t = Twitter()
    all_words = t.nouns(message)

    return set(all_words)


def count_words(training_set):
    '''단어별 빈도수를 세는 함수
    [스팸 여부, 메세지 내용]
    1 : adult
    2 : ETC
    3 : gambling
    4 : internet
    5 : loan
    0 : hams

    training_set : 학습 데이터

    return       : [스팸에서 나온 빈도, 햄에서 나온 빈도]
    '''
    counts = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    training_set_arr = training_set.values

    for is_spam, message in training_set_arr:
        for word in tokenize(message):
            counts[word][int(is_spam)] += 1

    return counts


def word_probabilities(counts,
                       totalNonSpams,
                       totalAdultSpams,
                       totalEtcSpams,
                       totalGamblingSpams,
                       totalInternetSpams,
                       totalLoanSpams,
                       k=0.5):
    '''반도수를 통해 확률값을 추정하는 함수
    return : 각 항목별 확률을 담은 리스트
    '''
    return [(w,
             (nonSpam + k) / (totalNonSpams + 2 * k),
             (adultSpam + k) / (totalAdultSpams + 2 * k),
             (etcSpam + k) / (totalEtcSpams + 2 * k),
             (gamblingSpam + k) / (totalGamblingSpams + 2 * k),
             (internetSpam + k) / (totalInternetSpams + 2 * k),
             (loanSpam + k) / (totalLoanSpams + 2 * k))
            for w, (nonSpam, adultSpam, etcSpam, gamblingSpam, internetSpam, loanSpam) in counts.items()]


def spam_probability(word_probs, message):
    '''스팸 확률을 계산하는 함수
    1 : adult
    2 : ETC
    3 : gambling
    4 : internet
    5 : loan
    0 : hams

    word_probs :
    message    :

    return     : 큰 가능성, 스팸 종류
    '''
    log_prob_if_adultSpam = 0.0
    log_prob_if_nonSpam = 0.0
    log_prob_if_etcSpam = 0.0
    log_prob_if_gamblingSpam = 0.0
    log_prob_if_internetSpam = 0.0
    log_prob_if_loanSpam = 0.0

    message_wrords = tokenize(message)

    for word, prob_if_nonSpam, prob_if_adultSpam, prob_if_etcSpam, \
            prob_if_gamblingSpam, prob_if_internetSpam, prob_if_loanSpam in word_probs:
        if word in message_wrords:
            log_prob_if_adultSpam += math.log(prob_if_adultSpam)
            log_prob_if_etcSpam += math.log(prob_if_etcSpam)
            log_prob_if_gamblingSpam += math.log(prob_if_gamblingSpam)
            log_prob_if_internetSpam += math.log(prob_if_internetSpam)
            log_prob_if_loanSpam += math.log(prob_if_loanSpam)
            log_prob_if_nonSpam += math.log(prob_if_nonSpam)

        else:
            log_prob_if_adultSpam += math.log(1.0 - prob_if_adultSpam)
            log_prob_if_etcSpam += math.log(1.0 - prob_if_etcSpam)
            log_prob_if_gamblingSpam += math.log(1.0 - prob_if_gamblingSpam)
            log_prob_if_internetSpam += math.log(1.0 - prob_if_internetSpam)
            log_prob_if_loanSpam += math.log(1.0 - prob_if_loanSpam)
            log_prob_if_nonSpam += math.log(1.0 - prob_if_nonSpam)

    prob_if_adultSpam = math.exp(log_prob_if_adultSpam)
    prob_if_etcSpam = math.exp(log_prob_if_etcSpam)
    prob_if_gamblingSpam = math.exp(log_prob_if_gamblingSpam)
    prob_if_internetSpam = math.exp(log_prob_if_internetSpam)
    prob_if_loanSpam = math.exp(log_prob_if_loanSpam)
    prob_if_nonSpam = math.exp(log_prob_if_nonSpam)

    max_prob = 0
    index_prob = ''

    if max_prob < (prob_if_loanSpam / (prob_if_loanSpam + prob_if_nonSpam)):
        max_prob = prob_if_loanSpam / (prob_if_loanSpam + prob_if_nonSpam)
        index_prob = 'loan'

    if max_prob < (prob_if_adultSpam / (prob_if_adultSpam + prob_if_nonSpam)):
        max_prob = prob_if_adultSpam / (prob_if_adultSpam + prob_if_nonSpam)
        index_prob = 'adult'

    if max_prob < (prob_if_etcSpam / (prob_if_etcSpam + prob_if_nonSpam)):
        max_prob = prob_if_etcSpam / (prob_if_etcSpam + prob_if_nonSpam)
        index_prob = 'etc'

    if max_prob < (prob_if_gamblingSpam / (prob_if_gamblingSpam + prob_if_nonSpam)):
        max_prob = prob_if_gamblingSpam / (prob_if_gamblingSpam + prob_if_nonSpam)
        index_prob = 'gambling'

    if max_prob < (prob_if_internetSpam / (prob_if_internetSpam + prob_if_nonSpam)):
        max_prob = prob_if_internetSpam / (prob_if_internetSpam + prob_if_nonSpam)
        index_prob = 'internet'

    return max_prob, index_prob


class NaiveBayesClassifier:
    def __init__(self, k=0.5):
        self.k = k
        self.word_probs = []

    def classify(self, message):
        return spam_probability(self.word_probs, message)

    def train(self, training_set):
        num_nonSpams = len(training_set[train_test.is_spam == '0'])
        num_adultSpams = len(training_set[train_test.is_spam == '1'])
        num_etcSpams = len(training_set[train_test.is_spam == '2'])
        num_gamblingSpams = len(training_set[train_test.is_spam == '3'])
        num_internetSpams = len(training_set[train_test.is_spam == '4'])
        num_loanSpams = len(training_set[train_test.is_spam == '5'])

        word_counts = count_words(training_set)
        self.word_probs = word_probabilities(
            word_counts,
            nun_nonSpams,
            num_adultSpams,
            num_etcSpams,
            num_gamblingSpams,
            num_internetSpams,
            num_loanSpams,
            self.k
        )


def p_spam_given_word(word_prob):
    word, prob_if_spam, prob_if_nonSpam = word_prob

    return prob_if_spam / (prob_if_spam + prob_if_nonSpam)


def train_and_test_model(data, sw, predictMess=''):
    if sw == '0':
        random.seed(0)
        train_data, test_data = train_test_split(data, test_size=0.25)

        print("train_data_cnt :", len(train_data))
        print("test_data_cnt :", len(test_data))

        classifier = NaiveBayesClassifier()
        classifier.train(train_data)

        test_data_arr = test_data.values
        classified = [
            (is_spam, message, classifier.classify(message))
            for is_spam, message in test_data_arr
        ]

        print(classified)

    else:
        random.seed(0)
        train_data, test_data = train_test_split(data, test_size=0)
        classifier = NaiveBayesClassifier()
        classifier.train(train_data)
        spam_probability = classifier.classify(predictMess)

        print(spam_probability)
        print(spam_probability[0])

        if spam_probability[0] > 0.5:
            category = ''

            if spam_probability[1] == "adult":
                category = "성인물"

            elif spam_probability[1] == "etc":
                category = "기타"

            elif spam_probability[1] == "gambling":
                category = "게임"

            elif spam_probability[1] == "internet":
                category = "인터넷유도"

            elif spam_probability[1] == "loan":
                category = "대출"

            print(category, "스팸 메세지 입니다. ", spam_probability[0])

        else:
            print("스팸 메세지가 아닙니다. ", spam_probability[0])


def nlpKoSpamStart(predictMessage, mode, trainCsvPath):
    '''
    0 : modeling
    1 : prediction
    '''
    trainCsvPath += "/train_result.csv"

    data = pd.read_csv(trainCsvPath)
    trainData = data.loc[:, ["is_spam", "message"]]

    train_and_test_model(trainData, mode, predictMess)
