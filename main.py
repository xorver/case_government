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


def analyze(words):
    process = subprocess.Popen(['java', '-jar', jar_path, 'plstem'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, _ = process.communicate(' '.join(words).encode('utf-8'))

    result = dict()
    forms = stdout.decode('utf-8').split('\n')[:-2]
    for form in forms:
        try:
            if form.split()[2].split(':') in result[form.split()[0]]:
                result[form.split()[0]] = result[form.split()[0]] + [form.split()[2].split(':')]
        except KeyError:
            result[form.split()[0]] = [form.split()[2].split(':')]

    return result


def get_noun(words, whole_analysis):
    for word in words:
        try:
            for analysis in whole_analysis[word]:
                if analysis[0] in ['subst', 'adj', 'ppas']:
                    return analysis
        except KeyError:
            pass
    return None

# read pap
with open("data/pap.txt") as file:
    text = file.read()
notice_text = re.split(r'#.*', text)
notice_words = [normalize_text(x) for x in notice_text]
big_notice = [word for notice in notice_words for word in notice][:500000]
print(str(0) + '/' + str(len(big_notice)))
whole_analysis = analyze(big_notice)

for i in range(len(big_notice)):
    if i % 1000 == 0:
        print(str(i) + '/' + str(len(big_notice)))
    if big_notice[i] in chosen_prepositions:
        analysis = get_noun(big_notice[i + 1: i + 1 + N], whole_analysis)
        if analysis:
            stats[big_notice[i]][analysis[2]] += 1

for elem in chosen_prepositions:
    print(elem)
    for type in stats[elem].keys():
        if '.' not in type:
            print('   ' + type + ' ' + str(stats[elem][type]))




