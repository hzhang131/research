from django.shortcuts import render_to_response
from haystack.query import SearchQuerySet
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import TemplateView, ListView
import json
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.index import create_in, open_dir, exists_in
from whoosh.searching import Searcher
from whoosh.qparser import QueryParser
import re
import sys
import sqlite3
from .models import Article, Related
from .prepro import prepro, suggest
import os
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import stringfilter
from django.utils.decorators import method_decorator
from termcolor import colored
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Index, Search
from py2neo import Graph
from time import sleep
import json
es = Elasticsearch()
register = template.Library()

graph = Graph("bolt://localhost:11005", auth=("neo4j", "230804"))
@register.filter(needs_autoescape=True)
# @stringfilter

class SRCView(ListView):
    model = Article
    template_name = 'cached.html'  
    def get_queryset(self):
        return Article.objects.all()

def process(request):
    ''' internal url, hidden from public'''
    if request.method == 'POST':
        print('here')
        string = "\"{% static \"/text/" + request.POST['title'] + ".txt\" %}\""
        # split string in javascript.
        return HttpResponse(string)

class SRFView(ListView):
    model = Article
    template_name = 'folder.html'
    def get_queryset(self):
        cats = {}
        titles = []
        relates = {}
        kids = {}
        mydir = './static/text/'
        filelist = [f for f in os.listdir(mydir)]
        nonefile = open(mydir + 'none.txt', 'w+')
        nonefile.write('<div id = "error" style = "text-align: center; vertical-align: middle; line-height: 555px;"> <p> <b> None Available </b> </p> </div>')
        nonefile.close()

        for f in filelist:
            os.remove(os.path.join(mydir, f))
        for e in Article.objects.all():
            # catfile = open(mydir + 'catlist' + '_'.join(e.authors.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+')
            # catstring = ""
            if e.categories == 'Article':
                with open(mydir + '_'.join(e.title.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+') as file:
                    e.title = e.title.replace('(', '').replace(')', '').replace('/', '')
                    string = "<iframe src=" + "\"https://en.m.wikipedia.org/wiki/" + '_'.join(e.title.replace('(', '').replace(')', '').replace('\\', '').split()) + "\" width=\"100%\" height=\"100%\" style = \"border:0;\"></iframe>"
                    file.write(string)
                    titles.append(e.title)
                    e.save()
            elif e.categories == 'Related':
                

                e.title = e.title.replace('(', '').replace(')', '').replace('/', '')
                e.authors = e.authors.replace('(', '').replace(')', '').replace('/', '')
                e.submitter = e.submitter.replace('\'', '')

                with open(mydir + 'cat_' + e.submitter + '.txt', 'w+') as file:
                    string = "<iframe src=" + "\"https://en.m.wikipedia.org/wiki/" + 'Category:' + 'Databases' + "\" width=\"100%\" height=\"100%\" style = \"border:0;\"></iframe>"
                    file.write(string)

                with open(mydir + 'relate_' + '_'.join(e.title.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+') as file:
                    print('writing', e.title)
                    string = "<iframe src=" + "\"https://en.m.wikipedia.org/wiki/"  + e.title + "\" width=\"100%\" height=\"100%\" style = \"border:0;\"></iframe>"
                    file.write(string)

                if e.authors not in cats:
                    cats[e.authors] = [e.submitter]
                else:
                    if e.submitter not in cats[e.authors]:
                        cats[e.authors].append(e.submitter)


                if e.submitter not in relates:
                    relates[e.submitter] = [e.title]
                else:
                    if e.title not in relates[e.submitter]:
                        relates[e.submitter].append(e.title)

                for key in cats:
                    # print(key, relates[cats[key][0]])
                    kids[key] = relates[cats[key][0]]
                    # print(cats[e.authors][0])
                e.save()
        for t in titles:          
            if t in cats:
                catfile = open(mydir + 'catlist' + '_'.join(t.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+')
                catstring = ""
                for item in cats.get(t):
                    catstring = catstring + "<div id = \"" + item  + "\" style = \"left: 4.5%; position: relative;\">"
                    catstring = catstring + "<p> <b>" + item + " </b> </p>\n"
                    catstring = catstring + "<div id = 'selector' style=\"top: 0%; height: 4.5%; width: 17%; background-color: #ff0000; position: relative; border-radius: 15px 50px 30px;\">\n"
                    catstring = catstring + "<form action=\"javascript:void(0);\" method=\"post\" id = \"viewcat_" + item + "\">\n"
                    catstring = catstring + '<input type="hidden" name="title" value="' + item + '"/>\n'
                    catstring = catstring + "<button type=\"submit\" class = 'haha' style = \" background: transparent; border: none; color: white; float: left; color: #f2f2f2; text-align: center; top: 20%; right: 8%; position: absolute; text-decoration: none; \" onclick = \"current_key = '" + item + "'; console.log('viewing ' + current_key);\" > View &#8658;</button>\n"
                    catstring = catstring + "</form>\n"
                    catstring = catstring + "</div>\n"
                    catstring = catstring + "</div>\n"
                catfile.write(catstring)
                catfile.close()
            else:
                catfile = open(mydir + 'catlist' + '_'.join(t.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+')
                catfile.write('<div id = "error" style = "text-align: center; vertical-align: middle; line-height: 555px;"> <p> <b> None Available </b> </p> </div>')
                catfile.close()
                catfile = open(mydir + 'kids' + '_'.join(t.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+')
                catfile.write('<div id = "error" style = "text-align: center; vertical-align: middle; line-height: 555px;"> <p> <b> None Available </b> </p> </div>')
                catfile.close()

        for key in relates:
            catfile = open(mydir + 'related' + key + '.txt', 'w+')
            catstring = ""
            for item in relates.get(key):
                if item in titles:
                    continue
                catstring = catstring + "<div id = \"" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split())  + "\" style = \"left: 4.5%; position: relative;\">\n"
                catstring = catstring + "<p> <b>" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + " </b> </p>\n"
                catstring = catstring + "<div id = 'selector' style=\"top: 0%; height: 4.5%; width: 60%; background-color: #00cc00; position: relative; border-radius: 15px 50px 30px;\">\n"
                catstring = catstring + "<form action=\"javascript:void(0);\" method=\"post\" id = \"viewrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n"
                print("<form action=\"javascript:void(0);\" method=\"post\" id = \"viewrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n")
                catstring = catstring + '<input type="hidden" name="title" value="' + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + '"/>\n'
                catstring = catstring + "<button type=\"submit\" class = 'haha' style = \" background: transparent; border: none; color: white; float: left; color: #f2f2f2; text-align: center; top: 20%; right: 8%; position: absolute; text-decoration: none; \" onclick = \"current_key = '" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "'; console.log('viewing ' + current_key);\" > View &#8658;</button>\n"
                catstring = catstring + "</form>\n"
                catstring = catstring + "<form action=\"javascript:void(0);\" method=\"post\" id = \"visitrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n"
                catstring = catstring + '<input type="hidden" name="title" value="' + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + '"/>\n'
                catstring = catstring + "<button type=\"submit\" class = 'haha' style = \" background: transparent; border: none; color: white; float: left; color: #f2f2f2; text-align: center; top: 20%; left: 8%; position: absolute; text-decoration: none; \" onclick = \"current_key = '" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "'; console.log('viewing ' + current_key);\" > Visit </button>\n"
                catstring = catstring + "</form>\n"
                catstring = catstring + "</div>\n"
                catstring = catstring + "</div>\n"
            catfile.write(catstring)
            catfile.close()

        for key in kids:
            catfile = open(mydir + 'kids' + '_'.join(key.replace('(', '').replace(')', '').replace('/', '').split()) + '.txt', 'w+')
            catstring = ""
            for item in kids.get(key):
                if item in titles:
                    continue
                catstring = catstring + "<div id = \"" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split())  + "\" style = \"left: 4.5%; position: relative;\">\n"
                catstring = catstring + "<p> <b>" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + " </b> </p>\n"
                catstring = catstring + "<div id = 'selector' style=\"top: 0%; height: 4.5%; width: 60%; background-color: #00cc00; position: relative; border-radius: 15px 50px 30px;\">\n"
                catstring = catstring + "<form action=\"javascript:void(0);\" method=\"post\" id = \"viewrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n"
                print("<form action=\"javascript:void(0);\" method=\"post\" id = \"viewrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n")
                catstring = catstring + '<input type="hidden" name="title" value="' + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + '"/>\n'
                catstring = catstring + "<button type=\"submit\" class = 'haha' style = \" background: transparent; border: none; color: white; float: left; color: #f2f2f2; text-align: center; top: 20%; right: 8%; position: absolute; text-decoration: none; \" onclick = \"current_key = '" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "'; console.log('viewing ' + current_key);\" > View &#8658;</button>\n"
                catstring = catstring + "</form>\n"
                catstring = catstring + "<form action=\"javascript:void(0);\" method=\"post\" id = \"visitrelate_" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "\">\n"
                catstring = catstring + '<input type="hidden" name="title" value="' + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + '"/>\n'
                catstring = catstring + "<button type=\"submit\" class = 'haha' style = \" background: transparent; border: none; color: white; float: left; color: #f2f2f2; text-align: center; top: 20%; left: 8%; position: absolute; text-decoration: none; \" onclick = \"current_key = '" + '_'.join(item.replace('(', '').replace(')', '').replace('/', '').split()) + "'; console.log('viewing ' + current_key);\" > Visit </button>\n"
                catstring = catstring + "</form>\n"
                catstring = catstring + "</div>\n"
                catstring = catstring + "</div>\n"
            catfile.write(catstring)
            catfile.close()

        return Article.objects.all()

class SRFNView(ListView):
    model = Article
    template_name = 'nodes.html'  
    def get_queryset(self): # new
        nodes = []
        edges = []
        art_lookup = {}
        cat_lookup = {}
        json_dict = {}
        with open('./article/templates/network.json', 'w') as file:
            for e in Article.objects.all():
                if e.categories == 'Keyword':
                    nodes.append({"name": e.title, "type": "Keyword"})
                elif e.categories == "Article":
                    nodes.append({"name": e.title, "type": "Article"})
                    edges.append({"source": 0, "target": len(nodes)-1})
                    art_lookup[e.title] = len(nodes)-1
                else:
                    if e.submitter not in cat_lookup:
                        nodes.append({"name": e.submitter, "type": "Category"})
                        edges.append({"source": art_lookup[e.authors], "target": len(nodes)-1})
                        cat_lookup[e.submitter] = len(nodes)-1
                    nodes.append({"name": e.title, "type": "Article"})
                    edges.append({"source": cat_lookup[e.submitter], "target": len(nodes)-1})

                    # print(e.title, e.abstract, e.categories, e.submitter, e.update_date, e.authors)
            json_dict['nodes'] = nodes
            json_dict['edges'] = edges
            # print(json_dict)
            json.dump(json_dict, file) 
        return Article.objects.all()



class HomePageView(TemplateView):
    template_name = 'home.html'

class SRView(ListView):
    model = Article
    template_name = 'search_results.html'  
    vectorizer, clf, ics, cis, id_abstract_pair, title_id_pair, id_title_pair, swd = prepro()
    def get_queryset(self): # new
        Article.objects.all().delete()
        query = self.request.GET.get('q')
        filter_ = self.request.GET.get('f')
        mode = self.request.GET.get('l')
        print(query, filter_, mode)
        print('mode char is', mode)
        if not mode:
            with open('./static/stack/main_stack.txt', 'w+') as file:
                file.write(query + ' ' + filter_ + '\n')
            with open('./static/stack/cursor.txt', 'w+') as file:
                file.write('0')
        elif mode == 'add':
            string = ''
            num = int()
            with open('./static/stack/main_stack.txt', 'r') as file:
                string = [i.strip('\n') for i in file] 
            with open('./static/stack/cursor.txt', 'r') as file:
                num = int(file.read())
            string = string[:num+1]
            string = '\n'.join(string) + '\n'
            with open('./static/stack/main_stack.txt', 'w+') as file:
                string += query + ' ' + filter_ + '\n'
                file.write(string)
            with open('./static/stack/cursor.txt', 'w+') as file:
                num += 1
                file.write(str(num))
        elif mode == 'back':
            num = int()
            with open('./static/stack/cursor.txt', 'r') as file:
                num = int(file.read())
            num = num - 1
            if num < 0:
                num = 0
            keylist = []
            with open('./static/stack/main_stack.txt', 'r') as file:
                keylist = [i.strip('\n') for i in file]
            query = keylist[num]
            with open('./static/stack/cursor.txt', 'w+') as file:
                file.write(str(num))
        elif mode == 'forward':
            num = int()
            total_cnt = int()
            keylist = []
            with open('./static/stack/main_stack.txt', 'r') as file:
                for _ in file:
                    total_cnt += 1
                    keylist.append(_.strip('\n'))
            with open('./static/stack/cursor.txt', 'r') as file:
                num = int(file.read())
            num = num + 1
            if num == total_cnt:
                num = total_cnt - 1
            with open('./static/stack/cursor.txt', 'w+') as file:
                file.write(str(num))
            query = keylist[num]


        print('started')
        search_list, related_list = generate(self.vectorizer, self.clf, self.ics, self.cis, self.id_abstract_pair, self.title_id_pair, self.id_title_pair, query, self.swd, filter_)
        print('finished')


        # title_list, abstract_list = get_whoosh_data(query)
        # for i in range(min(10, len(title_list))):
        #     article = Article()
        #     article.title = title_list[i]
        #     article.abstract = abstract_list[i]
        #     query_saved = query
        #     lst = re.findall(query, article.abstract, flags=re.IGNORECASE)
        #     for match in lst:
        #         article.abstract = article.abstract.replace(match, "<span style = \"color: purple\">%s</span>" % match)
        #     article.save()
        
        article = Article()
        article.title = query
        article.abstract = 'This is the keyword that we were searching for.'
        article.categories = 'Keyword'
        article.save()

        article = Article()
        article.title = filter_
        article.abstract = 'This is the filter that we are applying.'
        article.categories = 'Filter'
        article.save()

        for i in search_list:
            article = Article()
            article.title = i[0]
            article.abstract = i[1]
            # print('debug', article.abstract)
            article.categories = 'Article'
            # lst = re.findall(re.escape(query), article.abstract, flags=re.IGNORECASE)
            # for match in lst:
            #     article.abstract = article.abstract.replace(match, "<span style = \"color: purple\">%s</span>" % match)
            article.save()

        for i in related_list:
            article = Article()
            article.title = i[0]
            article.abstract = i[1]
            # print('debug', article.abstract)
            article.categories = 'Related'
            article.submitter = i[2]
            article.update_date = i[3]
            article.authors = i[4]
            # lst = re.findall(re.escape(query), article.abstract, flags=re.IGNORECASE)
            # for match in lst:
            #     article.abstract = article.abstract.replace(match, "<span style = \"color: purple\">%s</span>" % match)
            article.save()

        # add in the query_in and filter_ to article
        print('final')
        return Article.objects.all()

def get_whoosh_data(query):
    ix = open_dir("mysite/whooshdir")
    searcher = ix.searcher()
    results = searcher.find("abstract", query)
    title_list = []
    abstract_list = []
    count = 0
    for i in results:
        count += 1
        titles = i['title']
        title_list.append(titles)
        abstracts = i['abstract']
        abstract_list.append(abstracts)

    print(type(results), len(results), count)
    print('%d records found' % len(results))
    return title_list, abstract_list

def generate(vectorizer, clf, ics, cis, id_abstract_pair, title_id_pair, id_title_pair, x, swd, filter_):
    search_list = []
    related_list = []

    print(colored('-------------------Processing Level 2-------------------', 'magenta'))
    start = time.time()
    sample_sol = vectorizer.transform([x])
    keep_words, temp_out = suggest(x, vectorizer, clf, es, swd, filter_)
    if not keep_words:
        print(colored('No results Available', 'red'))
        sys.exit()

    # print(temp_out[0])
    sample = vectorizer.transform([temp_out[0]])
    sample_dense = sample.todense()
    bc = clf.predict_log_proba(sample_dense)
    benchmark = bc[0][1] - bc[0][0]

    print('checkpoint 1: time', time.time() - start)
    start = time.time()
    print(colored('-------------------Processing Level 2-------------------', 'magenta'))
    res = []
    used = []
    sample_sol = sample_sol.toarray()
    sample_sol = sample_sol.astype('float64')
    # for word in keep_words:
    #     if word in title_id_pair and title_id_pair.get(word) in ics and 'List' not in word:
    #         for termraw in ics.get(title_id_pair.get(word)):
    #             term = termraw.strip('\'')
    #             term = term.replace('_', ' ')
    #             if x in term:
    #                 continue
    #             for artid in cis.get(termraw):
    #                 if artid in id_abstract_pair:
    #                     sample = vectorizer.transform([id_abstract_pair.get(artid)])
    #                     sample_dense = sample.todense()
    #                     if clf.predict(sample_dense)[0] != '0' and artid in id_title_pair:
    #                         prob = clf.predict_log_proba(sample_dense)
    #                         score = prob[0][1] - prob[0][0]
    #                         title = id_title_pair.get(artid)
    #                         if title not in used:
    #                             res.append([title, score])
    #                             used.append(title)

    keep_words_copy = ['"' + i + '"' for i in keep_words]
    string = ','.join(keep_words_copy)
    print('checkpoint 2: time', time.time() - start)
    start = time.time()
    # for word in keep_words:
    #     tbl = graph.run('match (a:Article) - [:in] -> (c:Category) - [:consists] -> (e:Article)  where a.title = "%s"\
    #     return e.title as t, e.abstract as a' % word).to_table()
    #     tbl = np.array(tbl)
    #     for row in tbl:
    #         sample = vectorizer.transform([row[1]])
    #         sample_dense = sample.todense()
    #         response = clf.predict(sample_dense)[0]
    #         if response != '0':
    #             prob = clf.predict_log_proba(sample_dense)
    #             score = prob[0][1] - prob[0][0]
    #             if row[0] not in used:
    #                 res.append([row[0], score])
    #                 used.append([row[0]])
    if not filter_:
        if len(x.split()) <= 1:
            query = 'match (a:Article) - [:in] -> (c:Category_name) - [:consists] -> (e:Article)  where a.title in [%s] return distinct e.title as t, e.abstract as a, c.name as n, a.title as at' % string
        else:
            query = 'match (a:Article) - [:in] -> (c:Category_name) - [:consists] -> (e:Article)  where a.title in [{0}] and (e.abstract contains \"{1}\" or e.title contains \"{1}\") return distinct e.title as t, e.abstract as a, c.name as n, a.title as at'.format(string, x.split()[-1])
    else:
        query = 'match (a:Article) - [:in] -> (c:Category_name) - [:consists] -> (e:Article)  where a.title in [{0}] and (e.abstract contains \"{1}\" or e.title contains \"{1}\") return distinct e.title as t, e.abstract as a, c.name as n, a.title as at'.format(string, filter_)
   
    sleep(0.2)
    tbl = graph.run(query).to_table()
    tbl = np.array(tbl)
    # for row in tbl:
    #     if not row[1]:
    #         continue
    #     sample = vectorizer.transform([row[1]])
    #     sample_dense = sample.todense()
    #     response = clf.predict(sample_dense)[0]
    #     if response != '0':
    #         prob = clf.predict_log_proba(sample_dense)
    #         score = prob[0][1] - prob[0][0]
    #         if row[0] not in used:
    #             res.append([row[0], score, row[2], row[3]])
    #             # used.append([row[0]])
    #             used.append(row[0])

    arr = tbl[:, 1]
    sample = vectorizer.transform(arr)
    sample_dense = sample.todense()
    response_ = clf.predict(sample_dense).reshape(-1)
    indices = np.argwhere(response_ == '1')
    tbl = tbl[indices].reshape(len(indices), -1)
    N = len(indices)
    ones = (np.zeros(N) + 1).astype(int)
    first, second, third = tbl[:,0].reshape(-1, 1), ones.reshape(-1, 1), tbl[:,[2,3]].reshape(-1, 2)
    res = np.concatenate((first, second, third), axis=1)
    used = tbl[:,0]
    res = list(res)
    print('checkpoint 3: time', time.time() - start)
    start = time.time()

    sols = []
    print(colored('Here are some relevant search results:', 'green'))
    for idx, word in enumerate(keep_words):
        # print(colored(word, 'red'), '\n'+id_abstract_pair.get(title_id_pair.get(word)))
        # print(colored(word, 'red'), '\n'+ temp_out[idx])
        # sols.append(id_abstract_pair.get(title_id_pair.get(word)))
        sols.append(temp_out[idx])
        search_list.append((word, temp_out[idx]))
        # print(temp_out[idx])
    res1 = np.array(res)
    res1 = res1[:,0]

    for entry in range(len(res)):
        res[entry][1] = str(abs(int(res[entry][1])-benchmark))
        

    # res = list(res)
    res.sort(key=lambda x: x[1])
    # res.reverse()
    print('checkpoint 4: time', time.time() - start)
    start = time.time()

    print(colored('You might also be interested in:', 'blue'))
    start = time.time()
    flag = False
    new_res = []
    countset = set()
    for i in search_list:
        countset.add(i[0])
    
    count = 0

# old code starts...... redefined things in here.    
    # if es.indices.exists(index="test"):
    #     es.indices.delete(index="test")
    # print('benchmark 1 takes', time.time() - start)
    # print(list(np.unique(np.array(res)[:,0])))
    # start = time.time()
    # actions = []
    # for idx, row in enumerate(res):
    #     abs_ = graph.run('match (a:Article {title: "%s"}) return a.abstract' % row[0]).to_table()[0][0]
    #     actions.append({"_index": "test", "_id": idx, "title": row[0], "abstract": abs_, "category": row[2], "prev": row[3]})
    
    # helpers.bulk(es, actions)
    # sleep(0.5)
    # searched = es.search(index="test", body={"from": 0, "size": 100, "query": {"multi_match": {"query": filter_, "fields": ['title^2.0', 'category^10.0']}}})
    # if searched['hits']['max_score']:
    #     res = []
    #     print('rescored based on filter')
    #     for i in searched['hits']['hits']:
    #         res.append([i.get('_source').get('title'), i.get('_score'), i.get('_source').get('category'), i.get('_source').get('prev')])
    
    # print('benchmark 2 takes', time.time() - start)
    # start = time.time()
# old code ends...... redefined things in here.
# Databases
    print('checkpoint 5: time', time.time() - start)
    start = time.time()

    keep_words_dict = {}
    for idx, i in enumerate(res):
        if i[3] not in keep_words_dict:
            keep_words_dict[i[3]] = [i[0]]
        else:
            keep_words_dict[i[3]].append(i[0])
    
    print('checkpoint 6: time', time.time() - start)
    start = time.time()

    res = []
    keycounts = {}
    for key in keep_words_dict:
        k_list = keep_words_dict.get(key)
        if filter_:
            searched = es.search(index="ita", body={
                            "query": {
                                "bool":{
                                    "must":[
                                        {"terms": {
                                            "title.keyword": k_list }
                                        },
                                        
                                        {"match": {
                                            "title": filter_
                                            }
                                        }
                                    ]
                                }
                            }
                        })
        else:
            searched = es.search(index="ita", body={
                            "query": {
                                "bool":{
                                    "must":[
                                        {"terms": {
                                            "title.keyword": k_list }
                                        }
                                    ]
                                }
                            }
                        })
        for idx, i in enumerate(searched['hits']['hits']):
            if key in keycounts and keycounts[key] == 10:
                continue
            if key == i.get('_source').get('title'):
                continue
            if key not in keycounts:
                keycounts[key] = 1
            else:
                keycounts[key] += 1
            res.append([i.get('_source').get('title'), i.get('_score'), 'Databases_%s' % key.replace('(', '').replace(')', '').replace(' ', '_'), key])

    print('checkpoint 7: time', time.time() - start)
    start = time.time()

    # while len(new_res) < 10:
    #     if count >= len(res):
    #         break
    #     if res[count][0] not in countset:
    #         new_res.append(res[count])
    #         countset.add(res[count][0])
    #     count += 1
    new_res = res
    # print(new_res)

    for word in new_res:
        if keep_words[0] == word[0]:
            flag = True
            continue
        res_ = graph.run('match (a:Article {title: "%s"}) return a.abstract' % word[0]).to_table()
        if res_:
            res_ = res_[0][0]
        else:
            continue
        # related_list.append((word[0], id_abstract_pair.get(title_id_pair.get(word[0]))))
        related_list.append((word[0], res_, word[2], word[1], word[3]))
        # print(colored(word[0], 'red'), '\n'+id_abstract_pair.get(title_id_pair.get(word[0])))
        # print(colored(word[0], 'red'), '\n'+ res_)
    print('checkpoint 8: time', time.time() - start)
    start = time.time()

    print('here', len(related_list))

    if flag and len(res) > 10:
        try:
            res_ = graph.run('match (a:Article {title: "%s"}) return a.abstract' % res[11][0]).to_table()
            res_ = res_[0][0]
            # print(colored(res[11][0], 'red'), '\n', res_)
            related_list.append((res[11][0], res_, res[11][2], res[11][1], res[11][3]))
        except:
            print(res[11][0])

        # print(colored(res[11][0], 'red'), '\n'+id_abstract_pair.get(title_id_pair.get(res[11][0])))
        # print(colored(res[11][0], 'red'), '\n', res)
        # related_list.append((res[11][0], id_abstract_pair.get(title_id_pair.get(res[11][0]))))
        # related_list.append((res[11][0], res))
    print('checkpoint 9 takes', time.time() - start)
    start = time.time()
    print(len(search_list), len(related_list))
    return search_list, related_list
