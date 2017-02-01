
import json
import collections
import pymongo
import hashlib
from nltk.tokenize import RegexpTokenizer

client = pymongo.MongoClient()
counter = collections.Counter()

def load_thesaurus_file():

    with open('ea-thesaurus-lower.json') as normsf:
        norms = json.load(normsf)
    return norms


def tokenize_text_file(file):

    with open(file) as sample:
        samplewords = sample.read().lower()
        tokenizer = RegexpTokenizer(r'[\w\']+')
        tokenizedwords = tokenizer.tokenize(samplewords)
        counter.update(tokenizedwords)
    return tokenizedwords


def digest_file(file):

    with open(file) as sample:
        digest = sha_hash = hashlib.sha256(bytes(file, encoding='utf-8')).hexdigest()
    return digest


def check_for_associations(tokenised_file, thesaurus_file):

    not_found = []
    found = []
    for word in tokenised_file:
        #print(word)
        current = []
        try:
            for word_association in thesaurus_file[word][:3]:
                #print(word_association)
                current.append(word_association)
        except KeyError:
            not_found.append([word, counter[word]])
        found.append([word, counter[word], current])

    return {'found': found, 'not_found': not_found}


def build_document_and_upload(result, file):

    digest = digest_file(file)
    doc = {'fileKey': digest, 'result': result}
    db = client['wordAssociations']
    results = db.results
    if results.find_one({"fileKey": digest}):
        return "File Has Been Checked Before!"
    else:
        result_id = results.insert_one(doc).inserted_id
        return result_id

def check_db_for_file(file):

    digest = digest_file(file)
    db = client['wordAssociations']
    results = db.results
    post = results.find_one({"fileKey": digest})
    if post:
        return {'result_id': post.get('_id'), 'new': 'false'}
    else:
        return {'result_id': result_id, 'new': 'true'}

thesaurus = load_thesaurus_file()
tokenised = tokenize_text_file('sampletext2.txt')
result1 = check_db_for_file('sampletext2.txt')
print(result1.get('result_id'))
if result1.get('new'):
    print("Not new file")
else:
    print("New File")
result = check_for_associations(tokenised, thesaurus)
result_id = build_document_and_upload(result,'sampletext2.txt')
print(result_id)
# stringfound = str(result['found'])
# stringnotfound = str(result['not_found'])
#print("found: " + stringfound)
#print(counter)
# for w, c, a in result['found']:
#     print("word : " + w)
#     print("frequency : " + str(c))
#     for association in a :
#         print("Associated word : " + str(list(association.keys())) + ", Score: " + str(list(association.values())))





