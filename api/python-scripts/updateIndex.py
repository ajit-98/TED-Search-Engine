import pandas as pd  
import json 
import math
from pymongo import MongoClient
from preProcess import preProcess,preProcessUrl
#collection names of the transcripts and inverted index
TRANSCRIPT = 'transcript'
INDEX = 'index'
DB = 'tedtranscript'



#connect to database
client = MongoClient("mongodb://localhost:27017/") 
db = client[DB] 
transcript_collection = db[TRANSCRIPT]
json_transcripts = transcript_collection.find(no_cursor_timeout=True).sort('_id')



#function to merge two lists of dictionaries
# Needs to be tested
def merge(list1,list2,param=None):
    l1 = len(list1)
    l2 = len(list2)
    i=0
    j=0
    listout=[]
    if param == None:
        param = list1[0].keys()[0]

    while i<l1 and j<l2:
        if(list1[i][param]==list2[j][param]):
            listout.append(list1[i])
            i=i+1 
            j=j+1
        elif(list1[i][param]<list2[j][param]):
            listout.append(list1[i])
            i=i+1
        else:
            listout.append(list2[j])
            j=j+1 
    if i == l1:
        listout.append(list2[j:l2])
    else:
        listout.append(list1[i:l1])
    return listout
    




def updateIndex(mongo_db,inverted_index):
    index_collection = mongo_db[INDEX]
    for word in inverted_index.keys():
        word_lookup = index_collection.find_one({"word":word})
        if word_lookup is None:
            try:
                index_collection.insert_one(inverted_index[word])
            except Exception as e:
                print("Error inserting documents into database {}".format(e))
        else:
            new_doclist = merge(word_lookup['docList'],inverted_index[word]['docList'],param='docList')
            try:
                index_collection.update_one({"word":word},{"$set":{"docList":new_docList}})
            except Exception as e:
                print("Error inserting documents into database {}".format(e))

def createIndex(mongo_db,inverted_index):
    index_collection = mongo_db[INDEX]
    for word in inverted_index.keys():
        try:
            index_collection.insert_one(inverted_index[word])
        except Exception as e:
            print("Error inserting documents into database {}".format(e))

# pass mongoDB cursor object to init function
class InvertedIndex:
    def __init__(self,docs):
        self.docs = docs
        self.index = {}
        self.idf = {}
        self.docCount = 0
    def make_index(self):
        print("Building Index....")
        for doc in self.docs:
            self.docCount+=1
            id = doc['_id']
            print("Processing URL for doc {}".format(id))
            url = preProcessUrl(doc['url'])
            print("Processing transcript for doc {}".format(id))
            transcript = preProcess(doc['transcript'])
            for i in range(len(transcript)):
                word=transcript[i]
                if(word != ''):
                    if word not in self.index.keys(): #word has not been seen in any document
                        self.index[word] = {"word":word,"idf":1,"docList":[{'docid':id,'body':[i],'tf':1,'url':[]}]}
                    elif id != self.index[word]["docList"][-1]['docid']: #word has not been seen in the current document
                        self.index[word]["docList"].append({'docid':id,'body':[i],'tf':1,'url':[]})
                        self.index[word]["idf"] +=1 
                    else: #word has been seen before in the document
                        self.index[word]["docList"][-1]['body'].append(i) #append position of the word in the doc in the index 
                        self.index[word]["docList"][-1]['tf']+=1
            for i in range(len(url)):
                word = url[i]
                if word != '':
                    if word not in self.index.keys(): #word has not been seen in any document
                        self.index[word] = {"word":word,"idf":1,"docList":[{'docid':id,'body':[],'tf':1,'url':[i]}]}
                    elif id != self.index[word]["docList"][-1]['docid']: #word has not been seen in current document
                        self.index[word]["docList"].append({'docid':id,'body':[],'tf':1,'url':[i]})
                        self.index[word]["idf"] += 1 
                    else: #word has been seen before in the document
                        self.index[word]["docList"][-1]['url'].append(i)
                        self.index[word]["docList"][-1]['tf']+=1
        wordCount = 0
        for word in self.index.keys():
            wordCount+=1
            self.index[word]["idf"] = math.log(self.docCount/(self.index[word]["idf"]+1))
            #print(word + '....{}'.format(self.index[word]["idf"]))
        print("Index with {} words successfully made".format(wordCount))       
     
index = InvertedIndex(json_transcripts)
index.make_index()
print("Inserting Index Into Database")
createIndex(db,index.index)




