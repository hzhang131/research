import json
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.index import create_in, open_dir, exists_in
from whoosh.searching import Searcher
from whoosh.qparser import QueryParser
import re
import sys
import sqlite3
import os

# json_data = []
# json_file = "arxiv-metadata-oai-snapshot-2020-08-14.json"
# file = open(json_file)
# count = 0
print('---------reading data---------')
# for line in file:
#     json_line = json.loads(line)
#     data_insert = list()
#     string = str()
#     for key in json_line:
#         if key in ['submitter', 'authors', 'title', 'abstract', 'categories', 'update_date']:
#             insert = json_line.get(key)
#             if not json_line.get(key):
#                 insert = 'empty ' + key
#             data_insert.append(insert)
#             string += insert + '\t'
#     string += '\n'
#     json_data.append(data_insert)
#     count += 1
#     if count == 100000:
#         break
# print('checkpoint 1: length of data is', len(json_data))

print('---------creating whoosh schema and indices---------')

# schema = Schema(submitter=TEXT(stored=True),
#                 authors=TEXT(stored=True),
#                 title=TEXT(stored=True),
#                 abstract=TEXT(stored=True),
#                 categories=TEXT(stored=True),
#                 update_date=ID(stored=True)
#                 )
# ix = create_in('../Documents/whooshdir', schema)
#
# count = 0
# writer = ix.writer()
# for row in json_data:
#     count+= 1
#     if not count % 1000:
#         print(count)
#     if row:
#         submitter, authors, title, abstract, categories, update_date = \
#         row[0], row[1], row[2], row[4], row[3], row[5]
#     writer.add_document(submitter=submitter, authors=authors, title=title, abstract=abstract, categories=categories, update_date=update_date)
# writer.commit()
# print('checkpoint 2: number of rows added', count)

print('---------searching user defined keyword or phrases---------')
def query(input: str):
    ix = open_dir("whooshdir")
    print(exists_in("whooshdir"))
    searcher = ix.searcher()
    results = searcher.find("abstract", input)
    print('%d records found' % len(results))
    for i in range(min(5, len(results))):
        print(json.dumps(results[i].fields()['abstract'], ensure_ascii=False), '\n')

print('---------backend query finishes---------')
if __name__ == '__main__':
    query(sys.argv[1])
