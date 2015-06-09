import subprocess
import re
import collections

jar_path = 'data/morfologik-distribution-1.9.0/morfologik-tools-1.9.0-standalone.jar'
ignored_chars = {'$', '(', ',', '.', ':', ';', '0', '3', '3', '3', '4', '5',
                 '6', '7', '8', '9', '\\', '`', '\'', '+', '-', '*', '/', '<',
                 '>', '^', '%', '=', '?', '!', '[', ']', '{', '}', '_', '\n',
                 '"', '&', '~'}
chosen_prepositions = {'z', 'do', 'na', 'bez', 'za'}
N = 3
stats = {}
for prep in chosen_prepositions:
    stats[prep] = collections.Counter()


def normalize_text(text):
    text = text.lower()
    for pattern in ignored_chars:
        text = re.sub(re.escape(pattern), '', text)
    return text.split()


def analyze(word):
    echo_words = subprocess.Popen(['echo', word], stdout=subprocess.PIPE)
    analysis = subprocess.check_output(['java', '-jar', jar_path, 'plstem'], stdin=echo_words.stdout, stderr=subprocess.DEVNULL)
    echo_words.wait()
    forms = analysis.decode('utf-8').split('\n')[:-2]
    return [form.split()[2].split(':') for form in forms]


def get_noun(words):
    for word in words:
        for analysis in analyze(word):
            if analysis[0] == 'subst':
                return analysis
    return None

# read pap
with open("data/pap.txt") as file:
    text = file.read()
notice_text = re.split(r'#.*', text)
notice_words = [normalize_text(x) for x in notice_text]

for notice in notice_words:
    for i in range(len(notice)):
        if notice[i] in chosen_prepositions:
            analysis = get_noun(notice[i + 1: i + i + N])
            if analysis:
                stats[notice[i]][analysis[2]] += 1

for elem in chosen_prepositions:
    print(elem)
    for type in stats[elem].keys():
        print('   ' + type + ' ' + str(stats[elem][type]))




