# -- coding: utf-8 --
import subprocess
import re
import sys
import os

JAR_PATH = 'data/morfologik-distribution-1.9.0/morfologik-tools-1.9.0-standalone.jar'
IGNORED_CHARS = {'$', '(', ',', '.', ':', ';', '\\', '`', '\'', '+', '-', '*',
                 '/', '<', '>', '^', '%', '=', '?', '!', '[', ']', '{', '}',
                 '_', '"', '&', '~'}
IGNORED_SPECIAL = {'\n'}

main_word = sys.argv[1]


def normalize_text(text):
    text = text.lower()
    for pattern in IGNORED_CHARS:
        text = re.sub(re.escape(pattern), '', text)
    for pattern in IGNORED_SPECIAL:
        text = re.sub(pattern, ' ', text)
    text = re.sub('  ', ' ', text)
    return text.split()


def analyze(words):
    process = subprocess.Popen(['java', '-jar', JAR_PATH, 'plstem'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)

    stdout, _ = process.communicate(' '.join(words))

    result = dict()
    forms = stdout.split('\n')[:-2]
    for form in forms:
        try:
            if form.split()[2].split(':') in result[form.split()[0]]:
                result[form.split()[0]] = result[form.split()[0]] + [form.split()[2].split(':')]
        except KeyError:
            result[form.split()[0]] = [form.split()[2].split(':')]

    return result


def is_verb(word, whole_analysis):
    try:
        for analysis in whole_analysis[word]:
            if 'verb' in analysis:
                return True
        return False
    except KeyError:
        return False

def find_verb_to_verb_sentence_right(notice, i, whole_analysis):
    if i >= len(notice):
        return []
    if is_verb(notice[i], whole_analysis):
        return [notice[i]]
    return [notice[i]] + find_verb_to_verb_sentence_right(notice, i+1, whole_analysis)

def find_verb_to_verb_sentence_left(notice, i, whole_analysis):
    if i < 0:
        return []
    if is_verb(notice[i], whole_analysis):
        return [notice[i]]
    return find_verb_to_verb_sentence_left(notice, i-1, whole_analysis) + [notice[i]]

def print_sentence(sentence):
    print(' '.join(sentence))
    print('\n')



# read pap
with open("data/pap.txt", encoding='utf-8') as file:
    text = file.read()
notice_text = [notice for notice in re.split(r'#.*', text) if main_word in notice]
notice_words = [normalize_text(x) for x in notice_text if x != '']


for notice in notice_words:
    for i in range(len(notice)):
        word = notice[i]
        if main_word in word:
            whole_analysis = analyze(notice)
            sentence = find_verb_to_verb_sentence_left(notice, i-1, whole_analysis) + \
                       [word] + \
                       find_verb_to_verb_sentence_right(notice, i+1, whole_analysis)

            print_sentence(sentence)



