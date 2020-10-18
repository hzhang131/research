import pandas
import wikipediaapi
import wikipedia
import csv
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer
from sklearn.svm import OneClassSVM
import json
import re
import nltk
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from nltk.stem.porter import *
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from termcolor import colored
from scipy import spatial
from numpy import dot
from numpy.linalg import norm
import sys
import time
import wikipediaapi
import wikipedia
from termcolor import colored
from scipy import spatial
from numpy import dot
from numpy.linalg import norm
import sys
import time
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Index, Search
from py2neo import Graph
import os

def prepro():
    id_abstract_pair = {}
    title_abstract_pair = {}
    # print(os.path.exists('../wikipedia/id_title_abstract_updated.txt'))
    # with open('../wikipedia/id_title_abstract_updated.txt', 'r') as file:
    #
    #     for row in file:
    #         lst = row.split('\t')
    #         id_ = lst[0]
    #         abstract = lst[2]
    #         title = lst[1]
    #         id_abstract_pair[id_] = abstract
    #         title_abstract_pair[title] = abstract


    cis = {}
    # with open('../wikipedia/category_ids.txt', 'r') as file:
    #     print('3')
    #     for idx, row in enumerate(file):
    #         if not idx % 100000:
    #             print('3', idx)
    #         lst = row.split('\t')
    #         cat = lst[0]
    #         ids = lst[1:]
    #         ids = [i for i in ids if i in id_abstract_pair]
    #         if len(ids) < 500 and 'All' not in cat and 'Wikipedia' not in cat and 'Articles' not in cat and 'articles' not in cat \
    #             and 'dmy' not in cat and 'Pages' not in cat and 'mdy' not in cat and 'different' not in cat \
    #             and 'CS1' not in cat and 'Webarchive' not in cat and 'wikidata' not in cat and 'link' not in cat\
    #             and 'Wikidata' not in cat and 'Vague' not in cat and 'Use' not in cat and 'List' not in cat:
    #             # if 'Performing_arts' in cat:
    #             #     print(cat)
    #             cis[cat] = ids

    # print(list(cis.keys())[:50])

    ics = {}
    # with open('../wikipedia/id_categories.txt', 'r') as file:
    #     for idx, row in enumerate(file):
    #         if not idx % 1000000:
    #             print('2', idx)
    #         lst = row.split('\t')
    #         id_ = lst[0]
    #         if id_ in id_abstract_pair:
    #             id_ = lst[0]
    #             cats = [i for i in lst[1:] if i in cis]
    #             ics[id_] = cats

    title_id_pair = {}
    id_title_pair = {}
    # with open('../wikipedia/id_title_abstract_updated.txt', 'r') as file:
    #     for row in file:
    #         lst = row.split('\t')
    #         id_ = lst[0]
    #         title = lst[1]
    #         title_id_pair[title] = id_
    #         id_title_pair[id_] = title

    sw = ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are", "aren", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "couldn", "couldn't", "d", "did", "didn", "didn't", "do", "does", "doesn", "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn", "hadn't", "has", "hasn", "hasn't", "have", "haven", "haven't", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn", "isn't", "it", "it's", "its", "itself", "just", "ll", "m", "ma", "me", "mightn", "mightn't", "more", "most", "mustn", "mustn't", "my", "myself", "needn", "needn't", "no", "nor", "not", "now", "o", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "re", "s", "same", "shan", "shan't", "she", "she's", "should", "should've", "shouldn", "shouldn't", "so", "some", "such", "t", "than", "that", "that'll", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "ve", "very", "was", "wasn", "wasn't", "we", "were", "weren", "weren't", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "won", "won't", "wouldn", "wouldn't", "y", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "could", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've", "let's", "ought", "she'd", "she'll", "that's", "there's", "they'd", "they'll", "they're", "they've", "we'd", "we'll", "we're", "we've", "what's", "when's", "where's", "who's", "why's", "would", "able", "abst", "accordance", "according", "accordingly", "across", "act", "actually", "added", "adj", "affected", "affecting", "affects", "afterwards", "ah", "almost", "alone", "along", "already", "also", "although", "always", "among", "amongst", "announce", "another", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "apparently", "approximately", "arent", "arise", "around", "aside", "ask", "asking", "auth", "available", "away", "awfully", "b", "back", "became", "become", "becomes", "becoming", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "believe", "beside", "besides", "beyond", "biol", "brief", "briefly", "c", "ca", "came", "cannot", "can't", "cause", "causes", "certain", "certainly", "co", "com", "come", "comes", "contain", "containing", "contains", "couldnt", "date", "different", "done", "downwards", "due", "e", "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "except", "f", "far", "ff", "fifth", "first", "five", "fix", "followed", "following", "follows", "former", "formerly", "forth", "found", "four", "furthermore", "g", "gave", "get", "gets", "getting", "give", "given", "gives", "giving", "go", "goes", "gone", "got", "gotten", "h", "happens", "hardly", "hed", "hence", "hereafter", "hereby", "herein", "heres", "hereupon", "hes", "hi", "hid", "hither", "home", "howbeit", "however", "hundred", "id", "ie", "im", "immediate", "immediately", "importance", "important", "inc", "indeed", "index", "information", "instead", "invention", "inward", "itd", "it'll", "j", "k", "keep", "keeps", "kept", "kg", "km", "know", "known", "knows", "l", "largely", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely", "line", "little", "'ll", "look", "looking", "looks", "ltd", "made", "mainly", "make", "makes", "many", "may", "maybe", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "million", "miss", "ml", "moreover", "mostly", "mr", "mrs", "much", "mug", "must", "n", "na", "name", "namely", "nay", "nd", "near", "nearly", "necessarily", "necessary", "need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "ninety", "nobody", "non", "none", "nonetheless", "noone", "normally", "nos", "noted", "nothing", "nowhere", "obtain", "obtained", "obviously", "often", "oh", "ok", "okay", "old", "omitted", "one", "ones", "onto", "ord", "others", "otherwise", "outside", "overall", "owing", "p", "page", "pages", "part", "particular", "particularly", "past", "per", "perhaps", "placed", "please", "plus", "poorly", "possible", "possibly", "potentially", "pp", "predominantly", "present", "previously", "primarily", "probably", "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite", "qv", "r", "ran", "rather", "rd", "readily", "really", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "respectively", "resulted", "resulting", "results", "right", "run", "said", "saw", "say", "saying", "says", "sec", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sent", "seven", "several", "shall", "shed", "shes", "show", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly", "since", "six", "slightly", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specifically", "specified", "specify", "specifying", "still", "stop", "strongly", "sub", "substantially", "successfully", "sufficiently", "suggest", "sup", "sure", "take", "taken", "taking", "tell", "tends", "th", "thank", "thanks", "thanx", "thats", "that've", "thence", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "thereto", "thereupon", "there've", "theyd", "theyre", "think", "thou", "though", "thoughh", "thousand", "throug", "throughout", "thru", "thus", "til", "tip", "together", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "ts", "twice", "two", "u", "un", "unfortunately", "unless", "unlike", "unlikely", "unto", "upon", "ups", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "v", "value", "various", "'ve", "via", "viz", "vol", "vols", "vs", "w", "want", "wants", "wasnt", "way", "wed", "welcome", "went", "werent", "whatever", "what'll", "whats", "whence", "whenever", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "whim", "whither", "whod", "whoever", "whole", "who'll", "whomever", "whos", "whose", "widely", "willing", "wish", "within", "without", "wont", "words", "world", "wouldnt", "www", "x", "yes", "yet", "youd", "youre", "z", "zero", "a's", "ain't", "allow", "allows", "apart", "appear", "appreciate", "appropriate", "associated", "best", "better", "c'mon", "c's", "cant", "changes", "clearly", "concerning", "consequently", "consider", "considering", "corresponding", "course", "currently", "definitely", "described", "despite", "entirely", "exactly", "example", "going", "greetings", "hello", "help", "hopefully", "ignored", "inasmuch", "indicate", "indicated", "indicates", "inner", "insofar", "it'd", "keep", "keeps", "novel", "presumably", "reasonably", "second", "secondly", "sensible", "serious", "seriously", "sure", "t's", "third", "thorough", "thoroughly", "three", "well", "wonder", "a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "co", "op", "research-articl", "pagecount", "cit", "ibid", "les", "le", "au", "que", "est", "pas", "vol", "el", "los", "pp", "u201d", "well-b", "http", "volumtype", "par", "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a1", "a2", "a3", "a4", "ab", "ac", "ad", "ae", "af", "ag", "aj", "al", "an", "ao", "ap", "ar", "av", "aw", "ax", "ay", "az", "b1", "b2", "b3", "ba", "bc", "bd", "be", "bi", "bj", "bk", "bl", "bn", "bp", "br", "bs", "bt", "bu", "bx", "c1", "c2", "c3", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj", "cl", "cm", "cn", "cp", "cq", "cr", "cs", "ct", "cu", "cv", "cx", "cy", "cz", "d2", "da", "dc", "dd", "de", "df", "di", "dj", "dk", "dl", "do", "dp", "dr", "ds", "dt", "du", "dx", "dy", "e2", "e3", "ea", "ec", "ed", "ee", "ef", "ei", "ej", "el", "em", "en", "eo", "ep", "eq", "er", "es", "et", "eu", "ev", "ex", "ey", "f2", "fa", "fc", "ff", "fi", "fj", "fl", "fn", "fo", "fr", "fs", "ft", "fu", "fy", "ga", "ge", "gi", "gj", "gl", "go", "gr", "gs", "gy", "h2", "h3", "hh", "hi", "hj", "ho", "hr", "hs", "hu", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ic", "ie", "ig", "ih", "ii", "ij", "il", "in", "io", "ip", "iq", "ir", "iv", "ix", "iy", "iz", "jj", "jr", "js", "jt", "ju", "ke", "kg", "kj", "km", "ko", "l2", "la", "lb", "lc", "lf", "lj", "ln", "lo", "lr", "ls", "lt", "m2", "ml", "mn", "mo", "ms", "mt", "mu", "n2", "nc", "nd", "ne", "ng", "ni", "nj", "nl", "nn", "nr", "ns", "nt", "ny", "oa", "ob", "oc", "od", "of", "og", "oi", "oj", "ol", "om", "on", "oo", "oq", "or", "os", "ot", "ou", "ow", "ox", "oz", "p1", "p2", "p3", "pc", "pd", "pe", "pf", "ph", "pi", "pj", "pk", "pl", "pm", "pn", "po", "pq", "pr", "ps", "pt", "pu", "py", "qj", "qu", "r2", "ra", "rc", "rd", "rf", "rh", "ri", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "rv", "ry", "s2", "sa", "sc", "sd", "se", "sf", "si", "sj", "sl", "sm", "sn", "sp", "sq", "sr", "ss", "st", "sy", "sz", "t1", "t2", "t3", "tb", "tc", "td", "te", "tf", "th", "ti", "tj", "tl", "tm", "tn", "tp", "tq", "tr", "ts", "tt", "tv", "tx", "ue", "ui", "uj", "uk", "um", "un", "uo", "ur", "ut", "va", "wa", "vd", "wi", "vj", "vo", "wo", "vq", "vt", "vu", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y2", "yj", "yl", "yr", "ys", "yt", "zi", "zz"]

    graph = Graph("bolt://localhost:11005", auth=("neo4j", "230804"))
    # sw = stopwords.words("english")
    swd = Counter(sw)
    # process the training dataset.
    # topic distribution: 50% CS, 50% non-CS.
    # More automotives, politicans and non-CS scientists.
    # Sports events, history, zoology. flora and fauna.
    # Divided_regions, Social institutions, Music and musicians
    noncs_list = []
    topics = ['Performing_arts', 'Visual_arts', 'Natural_sciences', 'Home_economics', 'Linguistics', 'Literature',
            'Law-related_lists', 'Philosophy', 'Theology', 'Anthropology', 'Archaeology', 'Archaeology', 'Geography', 'Political_science'
            ,'Cognitive_science', 'Sociology', 'Social_work', 'Biology', 'Chemistry', 'Earth_sciences', 'Space_science', 'Physics', 'Mathematics', 'Statistics', 'Business',
            'Chemical_engineering', 'Civil_engineering', 'Materials_science', 'Mechanical_engineering', 'Systems_science', 'Advertising', 'Music_genres', 'Car_ classifications'
            ,'21st-century_politicians', 'Sports_terminology', 'Zoology', 'Plant_subfamilies', '21st-century_social_scientists', 'Countries_in_Asia', 'Car_brands',
            'Military_technology', 'Journalism', 'Geography_of_the_United_States', 'Music', 'Types_of_university_or_college', 'Political_scandals', 'Finance',
            'Public_safety_ministries', 'Banking', 'Foods', 'Mountains', 'Performance_art_venues', 'Rivers', 'Acting', 'Current_shows', 'Ammunition', 'Film_genres', 'Naval_ warfare_tactics',
            'Snake_genera']

    # topics = ['\'' + i + '\'' for i in topics]
    topics = ['\"\'' + i + '\'\"' for i in topics]
    query = '[' + ','.join(topics) + ']'
    tbl = graph.run('match (a:Article) -[:in] -> (b:Category_name) where b.name in %s return a.title, a.abstract' % query).to_table()
    tbl = np.array(tbl)
    out_noncs = []
    for row in tbl:
        if 'Wikipedia' in row[0] or 'Template' in row[0] or 'Category' in row[0] or not row[1]:
            continue
        else:
            string = row[1]
            string = string.replace(re.escape(row[0]), '***')
            string = re.sub(r'\(.*?\)', '', string)
            if not string:
                continue
            string = string.lower()
            string = ' '.join([word for word in string.split() if word not in swd])
            out_noncs.append(string)

    # for i in topics:
    #     # string = 'Category:'+ i
    #     # wiki_wiki = wikipediaapi.Wikipedia('en')
    #     # dic = wiki_wiki.page(string).categorymembers
    #     print(i, i in cis)
    #     if i in cis:
    #         dic = cis[i]
    #         dic = [id_title_pair.get(j) for j in dic if j in id_title_pair]
    #         noncs_list += [key for key in dic if 'Wikipedia' not in key and 'Template' not in key and 'Category' not in key]
    #     else:
    #         continue
    #     # noncs_list += [key for key in dic if 'Wikipedia' not in key and 'Template' not in key and 'Category' not in key]
    #
    # out_noncs = {}
    # for idx, i in enumerate(noncs_list):
    #     if not idx % 100:
    #         print(i)
    #     if i in noncs_list and i not in out_noncs and i in title_abstract_pair:
    #         out_noncs[i] = title_abstract_pair.get(i).replace(i, '***')
    #         out_noncs[i] = re.sub(r'\(.*?\)', '', out_noncs[i])
    #         out_noncs[i] = out_noncs[i].lower()
    #         out_noncs[i] = ' '.join([word for word in out_noncs[i].split() if word not in swd])
    #
    # len(out_noncs)

    cs_list = []
    topics = ['Artificial_intelligence', 'Computational_science', 'Computer_graphics', 'Computer_architecture', 'Computer_security', 'Analysis_of_algorithms',
            'Algorithms', 'Theoretical_computer_science', 'Human-computer_interaction', 'Human-based_computation', 'Mathematical_optimization', 'Programming_languages', 'Type_theory', 'Concurrency_control'
            ,'Formal_methods', 'Database_theory', 'Software_engineering', 'Theory_of_computation', 'Embedded_systems', 'Computer_scientists', 'Computer_networking', 'Computer_hardware', 'Unsolved_problems_in_computer_ science', 'Software', 'Computational_geometry',
            'Computer_systems', 'Computer_science_education', 'Distributed_computing', 'Computer_science_organizations', 'Computer_science_conferences', 'Programming_contests', 'Data_mining', 'Compiler_optimizations', 'Data_modeling_languages']
    # topics = ['\'' + i + '\'' for i in topics]
    topics = ['\"\'' + i + '\'\"' for i in topics]
    query = '[' + ','.join(topics) + ']'
    tbl = graph.run('match (a:Article) -[:in] -> (b:Category_name) where b.name in %s return a.title, a.abstract' % query).to_table()
    tbl = np.array(tbl)
    out_cs = []
    for row in tbl:
        if 'Wikipedia' in row[0] or 'Template' in row[0] or 'Category' in row[0] or not row[1]:
            continue
        else:
            string = row[1]
            string = string.replace(re.escape(row[0]), '***')
            string = re.sub(r'\(.*?\)', '', string)
            if not string:
                continue
            string = string.lower()
            string = ' '.join([word for word in string.split() if word not in swd])
            out_cs.append(string)

    # for i in topics:
    #     # string = 'Category:'+ i
    #     # wiki_wiki = wikipediaapi.Wikipedia('en')
    #     # dic = wiki_wiki.page(string).categorymembers
    #     print(i, i in cis)
    #     if i in cis:
    #         print('true')
    #         dic = cis[i]
    #         dic = [id_title_pair.get(j) for j in dic if j in id_title_pair]
    #         print(dic[0])
    #         cs_list += [key for key in dic if 'Wikipedia' not in key and 'Template' not in key and 'Category' not in key]
    #     else:
    #         continue
    # out_cs = {}
    # for idx, i in enumerate(cs_list):
    #     if not idx % 100:
    #         print(i)
    #     if i in cs_list and i not in out_cs and i in title_abstract_pair:
    #         out_cs[i] = title_abstract_pair.get(i).replace(i, '***')
    #         out_cs[i] = re.sub(r'\(.*?\)', '', out_cs[i])
    #         out_cs[i] = out_cs[i].lower()
    #         out_cs[i] = ' '.join([word for word in out_cs[i].split() if word not in swd])
    # len(out_cs)


    training_tuples = []
    # cs is 1, non_cs is 0.
    for key in out_noncs:
        # training_tuples.append([out_noncs.get(key), 0])
        training_tuples.append([key, 0])
    for key in out_cs:
        # training_tuples.append([out_cs.get(key), 1])
        training_tuples.append([key, 1])
    training_tuples = np.array(training_tuples)
    np.random.shuffle(training_tuples)
    x_train, y_train = [], []
    for i in training_tuples:
        x_train.append(i[0])
        y_train.append(i[1])
    print(len(y_train))


    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df = 20)
    X = vectorizer.fit_transform(x_train)
    Y = np.array(y_train)

    kf = KFold(n_splits=2)
    a, b, c, d = [], [], [], []

    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        Y_train, y_test = Y[train_index], Y[test_index]
        clf = GaussianNB()
        clf.fit(X_train.todense(), Y_train)
        y_pred = clf.predict(X_test.todense())
        a.append(f1_score(y_test, y_pred, average="macro"))
        b.append(precision_score(y_test, y_pred, average="macro"))
        c.append(recall_score(y_test, y_pred, average="macro"))
        d.append(accuracy_score(y_test, y_pred))

    # print('f1 ', np.mean(a))
    # print('precision ', np.mean(b))
    # print('recall ', np.mean(c))
    # print('accuracy ', np.mean(d))

    X_train, X_test = X[:len(Y)//2], X[len(Y)//2:]
    Y_train, Y_test = Y[:len(Y)//2], Y[len(Y)//2:]

    clf = GaussianNB()
    # clf.fit(X.todense(), Y)

    clf.fit(X_train.todense(), Y_train)
    Y_pred = clf.predict(X_test.todense())
    accuracy_score(Y_test, Y_pred)

    return vectorizer, clf, ics, cis, id_abstract_pair, title_id_pair, id_title_pair, swd

def suggest(query_in, vectorizer, clf, es, swd, filter_):
    start = time.time()
    # , 'abstract^10.0'
    print(colored('start searching ', 'magenta'))
    if filter_:
        res = es.search(index="ita", body={"from": 0, "size": 100, "query": {"multi_match": {"query": query_in +'^5' + ' %s' %filter_, "fields": ['title^10.0', 'abstract^1.0']}}})
    else:
        res = es.search(index="ita", body={"from": 0, "size": 100, "query": {"multi_match": {"query": query_in, "fields": ['title^10.0', 'abstract^1.0']}}})
    print(colored('done searching ', 'magenta'))
    summary_list = []
    trained_list = []
    words = []

    for i in res['hits']['hits']:
        if i.get('_source').get('abstract'):
            raw = i.get('_source').get('abstract')
            processed = re.sub(r'\(.*?\)', '', raw)
            processed = processed.lower()
            processed = ' '.join([word for word in processed.split() if word not in swd])
            trained_list.append(processed)
            summary_list.append(raw)
            words.append(i.get('_source').get('title'))

    if not summary_list:
        print(colored('No results Available', 'red'))
        sys.exit()

    trained_list = np.array(trained_list)
    transformed = vectorizer.transform(trained_list)
    y = clf.predict(transformed.todense())
    keep_words = []
    temp_out = []

    for idx in range(len(y)):
        if int(y[idx]) == 1 and 'List' not in words[idx]:
            temp_out.append(summary_list[idx])
            keep_words.append(words[idx])

    print('DONE', time.time() - start)
    return keep_words[:10], temp_out[:10]
