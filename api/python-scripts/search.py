from preProcess import preProcess,preProcessUrl
from pymongo import MongoClient
from dataStructures import MinHeap
import numpy as np
import math
import sys
import json
import time
from bson.objectid import ObjectId
import pika
import copy
#collection names of the transcripts and inverted index
TRANSCRIPT = 'transcript'
INDEX = 'index'
DB = 'tedtranscript'
#connect to database
client = MongoClient("mongodb://localhost:27017/") 
db = client[DB] 
index_collection = db[INDEX]
transcript_collection = db[TRANSCRIPT]

def sigmoid(x):
    return 1/(1+np.exp(-x))
def tanh(x):
    return (np.exp(x)-np.exp(-x))/(np.exp(x)+np.exp(-x))

def sort_tuple(tup):  
  
    # reverse = None (Sorts in Ascending order)  
    # key is set to sort using second element of  
    # sublist lambda has been used  
    return(sorted(tup, key = lambda x: x[1]))   
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



def rankDocs(query,index_collection=index_collection):
    query = preProcess(query) #preProcess query the same way as documents during indexing
    if query == []:
        return None
    mongo_query = [] 
    for token in query:
        mongo_query.append({"word":token})
    docs_cursor = index_collection.find({"$or":mongo_query})
    #sort docs retrieved from db in the order of the query ie query = q1,q2,q3 and query_results = [d1,d2,d3]
    keywordstodoc = {} 
    for doc in docs_cursor:
        keywordstodoc[doc["word"]] = (doc["docList"],doc["idf"]) 
    docptrs = [[0,False] for i in range(len(query))]
    isEmpty = 0
    for i in range(len(query)):
        if query[i] not in list(keywordstodoc.keys()):
            docptrs[i] = [0,True]
            keywordstodoc[query[i]] = None
            isEmpty +=1
    if isEmpty == len(query):
        print("Could not find any documents for your query please check spelling or rephrase your search")
        return None
    minHeap = MinHeap(len(query)+1,param=1,type='ObjectId')
    isTraversed = False

    for i in range(len(query)):
        if docptrs[i][1] == False:
            doctoinsert = keywordstodoc[query[i]][0][0]#insert first document corresponding to every keyword in query into the minHeap
            minHeap.insert((i,doctoinsert["docid"]))
    minHeap.minHeap()
    minDoc = minHeap.min() #smallest document in the heap 
    scoreDoc = [[minDoc[0],docptrs[minDoc[0]][0]]] #list of the common documents, each entry in the list contains a list with query number and the corresponding position of the document in the doclist
    scores = []
    max_substrings= {} #dictionary mapping each substring present in every document to the maximum number of times it occurs over all documents,to be used for scoring docs
    while isTraversed == False:
        query_number = minDoc[0] #find the query associated with the smallest document
        smallest_query = query[query_number]
        docptrs[query_number][0] +=1 #increment pointer to the docList associated with that query
        docptr = docptrs[query_number][0] 
        if docptr == len(keywordstodoc[query[query_number]][0]):
            docptrs[query_number][1] = True #if docptr associated with the query has reached the end of the docList set flag to True
            minHeap.remove() #remove the root of the minHeap and heapify #check if pointer has reached the end of the doclist of the query#replace root of minHeap with the next doc in the doclist
        else:
            minHeap.removeandreplace((query_number,keywordstodoc[smallest_query][0][docptr]["docid"]))
        newminDoc = minHeap.min() # get the new smallest document in the heap after heapifying
        
        if minDoc[1] == newminDoc[1]: #check if the smallest document is the same as the previous smallest
            scoreDoc.append([newminDoc[0],docptrs[newminDoc[0]][0]]) #if true append the query number and the index of the smallest document in that doclist to scoreDoc
            minDoc = newminDoc
        else:
            score = getScore(scoreDoc,query,keywordstodoc) #if the smallest document has changed, score the document
            scores.append(score) 
            minDoc = newminDoc
            scoreDoc = [[newminDoc[0],docptrs[minDoc[0]][0]]] #create new scoreDoc list as the smallest document has changed
        query_counter = 0
        for ptr in docptrs: #check if all the doclists have been fully traversed
            if ptr[1]==True:
                query_counter+=1
        if query_counter == len(query):
            isTraversed = True
    return sort_tuple(scores)
    #return scores

#score doc is a list containing the position
                
def getScore(scoreDoc,query,queryIndex,url_body_weight = [0.95,0.05],c1=7,c2=0.05):
    docid = queryIndex[query[scoreDoc[0][0]]][0][scoreDoc[0][1]]["docid"]
    query_vector = np.zeros(len(query)) #construct query vector,which contains the idf of each keyword in the query
    idf_sum=0
    url_score = 0
    body_score = 0  
    for i in range(len(query)):
        if queryIndex[query[i]] is not None:
            query_vector[i] += queryIndex[query[i]][1] #add the idf to the query vector
            idf_sum+=queryIndex[query[i]][1]
    query_norm = np.linalg.norm(query_vector)
    urlpositions = [None for i in range(len(query))] # list of all the positions of each query keyword in the document to be scored
    docpositions = [None for i in range(len(query))]
    pos_ptrs = [[0,True] for i in range(len(query))] # pointers to the positions of each query keyword in the document, to be used for linear merge
    tfidfs = [0 for i in range(len(query))] #tfidf values for everykeyword in the query
    for doc in scoreDoc:
        query_position = doc[0]
        doc_position = doc[1]
        urlpositions[query_position] = queryIndex[query[query_position]][0][doc_position]["url"]
        docpositions[query_position] = queryIndex[query[query_position]][0][doc_position]["body"]
        tfidfs[query_position] = queryIndex[query[query_position]][1] * queryIndex[query[query_position]][0][doc_position]["tf"] #idf*tf
        pos_ptrs[query_position] = [0,False] #if keyword is present in the query in either URL or doc set pos_ptrs to false
    for i in range(2): #score both url positions and doc positions 
        substring_parameters = {} #dictionary mapping each substring in the document to some metadata about the substring like length, idf values, number of occurences
        if i%2==0:
            positions = urlpositions
        else:
            positions = docpositions
        minHeap = MinHeap(len(query)+1,param=1,type='int') 
        isTraversed = False
        ptrs = copy.deepcopy(pos_ptrs)
        string = "" 
        N = 0 # number of substrings
        distances = [0] #list of all the distance between each consecutive substring in the document
        isEmpty = 0 #flag to indicate whether the document does not contain any keywords
        for j in range(len(query)): #initialize minHeap
            if positions[j] is not None and positions[j]:
                minHeap.insert((j,positions[j][0]))
            else:
                ptrs[j][1] = True # if keyword is not present in url or doc set ptrs to false
                isEmpty+=1
        if isEmpty != len(query):    
            minHeap.minHeap()
            substring_vector = np.zeros(len(query)) #vector of each substring of the query present in the doc
            substring_start = minHeap.min() #start of the substring in the document
            current_position = substring_start #minimum value of the minHeap
            string += query[current_position[0]]
            substring_weight = 1 #counts the number of keywords of the query are withing the substring
            substring_vector[substring_start[0]]+= query_vector[substring_start[0]]
        else:
            isTraversed = True
        while isTraversed == False: #find all substrings, compute doc vector and final score for the document and query pair       
            query_position = current_position[0] #query index corresponding to the minimum position in the heap
            ptrs[query_position][0]+=1 
            doc_ptr = ptrs[query_position][0]
            if doc_ptr == len(positions[query_position]): # if docptr has reached the end of the list set ptr to true
                ptrs[query_position][1] = True
                minHeap.remove()
            else:
                minHeap.removeandreplace((query_position,positions[query_position][doc_ptr]))
            if minHeap.min()[1] == current_position[1]: #if minimum position in the heap is equal to the previous minimum, then two keywords in the query are the sam
                query_position = minHeap.min()[0] #increment pointer to positions of the second occurence of the query and heapify to see if it present in the doc
                ptrs[query_position][0]+=1
                doc_ptr = ptrs[query_position][0]
                if doc_ptr == len(positions[query_position]):
                    ptrs[query_position][1] = True
                    minHeap.remove()
                else:

                    minHeap.removeandreplace((query_position,positions[query_position][ptrs[query_position][0]]))

            if minHeap.min()[0] == current_position[0]+1 and minHeap.min()[1] == current_position[1]+1: #if minimum position in the heap is the current position + 1 then a new substring has been found
                current_position = minHeap.min()
                substring_vector[current_position[0]]+=query_vector[current_position[0]]
                string += query[current_position[0]]
                substring_weight +=1

            else: #calculate vector for the substring and find the next one
                N+=1
                current_position = minHeap.min()
                if(current_position[0] !=-1):
                    distances.append(current_position[1] - substring_start[1])
                if string not in substring_parameters.keys() and string != '':
                    substring_parameters[string] = [np.sum(substring_vector),substring_weight,1] 
                else:
                    substring_parameters[string][2]+=1
                string = query[current_position[0]]
                substring_weight = 1
                substring_vector = np.zeros(len(query))
                substring_start = current_position 
                substring_vector[current_position[0]] += query_vector[current_position[0]]
            query_counter = 0
            for ptr in ptrs: #check if all position lists have been traversed
                if ptr[1] == True:
                    query_counter+=1
            if query_counter == len(query):
                isTraversed = True
        substring_scores = [[0,0] for i in range(len(query))] #list of lists recording the diversity and the substring score of each substring
        for key in substring_parameters.keys():
            substring_size = substring_parameters[key][1]
            num_of_occurences = substring_parameters[key][2]
            substring_idf_sum = substring_parameters[key][0]
            substring_scores[substring_size-1][1] +=num_of_occurences*substring_idf_sum/idf_sum
            substring_scores[substring_size-1][0] +=1/(len(query)-substring_size+1) 
        for k in range(len(query)-1,-1,-1):
            score = c1*substring_scores[k][0] + c2* substring_scores[k][1] #c1*diversity + c2*idf weighted frequency 
            if k == len(query) -1:
                alpha = 0.6
                if i%2 == 0:
                    url_score += alpha*score
                else:
                    body_score += alpha*score
            elif k == len(query)-2:
                alpha = 0.08
                if i%2==0:
                    url_score += alpha*score
                else:
                    body_score+=alpha*score
            else:
                alpha = alpha/1.1
                if i%2==0:
                    url_score+=alpha*score
                else:
                    body_score += alpha*score
        final_score = url_body_weight[0]*url_score + url_body_weight[1]*body_score
        avg_distance = np.mean(distances) #use later
    return docid,tanh(final_score)
                            

def nodeWorker(query):
    scores = rankDocs(query,index_collection)
    transcripts = []
    highest_docs = []
    count = 0
    if scores == None:
        return JSONEncoder().encode({"query":query,"docList":[]})
    for docid,score in scores[::-1][0:20]:
        count+=1
        highest_docs.append(docid)
    return JSONEncoder().encode({"query":query,"docList":highest_docs})
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ProcQuery',exchange_type='direct')
    channel.queue_declare(queue='Query')
    channel.queue_declare(queue='DocList')
    channel.queue_bind(exchange='ProcQuery',queue='Query',routing_key='Send')
    channel.queue_bind(exchange='ProcQuery',queue='DocList',routing_key='Recieve')


    def callback(ch, method, properties, body):
        print('Python has recieved message {}'.format(type(body)))
        message = nodeWorker(str(body,'utf-8'))
        channel.basic_publish(exchange='ProcQuery',routing_key='Recieve',body=message)
        print("Sent data to Node controller....")
    channel.basic_consume(queue='Query',auto_ack=True,on_message_callback=callback)
    print('Python ready to process queries')
    channel.start_consuming()

if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    
           


    







   


    


         
    
    



     





