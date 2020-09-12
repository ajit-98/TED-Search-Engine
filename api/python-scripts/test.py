import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
def main():

    channel.exchange_declare(exchange='ProcQuery',exchange_type='direct')
    channel.queue_declare(queue='Query')
    channel.queue_declare(queue='DocList')
    channel.queue_bind(exchange='ProcQuery',queue='DocList',routing_key='Recieve')
    channel.queue_bind(exchange='ProcQuery',queue='Query',routing_key='Send')


    def callback(ch, method, properties, body):
        print('Message recieved from queue {}'.format(type(body)))
    channel.basic_consume(queue='DocList',auto_ack=True,on_message_callback=callback)
    channel.start_consuming()
if __name__=="__main__":
    channel.basic_publish(exchange = 'ProcQuery',routing_key='Send',body='economic case')
    print('Message Sent')
    main()

'''
def stats():
    with open("query_results.txt",'a',encoding='utf-8') as f:
    f.writelines("{}. DOC ID: {}\n".format(count,docid))
    f.writelines("SCORE: {}\n".format(score))
    f.writelines("URL: {}\n".format(doc["url"]))
    f.writelines(doc["transcript"][0:2000]+'\n')
    f.writelines("-----------------------\n")
        




        
        num_substrings = []
        avg_distances = []
        with open("stats.txt",'w') as f:
            for statistic in stats:
                query_vector = statistic["query_vector"]
                f.writelines("DOCID {}\n".format(statistic['docid']))
                f.writelines("Query Vector is : {}\n".format(np.array2string(query_vector)))
                f.writelines("Number of substrings found are: {}\n".format(statistic["num_substrings"]))
                num_substrings.append(statistic["num_substrings"])
                f.writelines("Substrings are\n")
                count = 0
                for word in statistic["words"].keys():
                    count+=1
                    urlcount = statistic["words"][word]["urlcount"]
                    doccount = statistic["words"][word]["doccount"]
                    avgurldist = statistic["words"][word]["avg_url_distance"]
                    avgdocdist = statistic["words"][word]["avg_doc_distance"]
                    vector = np.array2string(statistic["words"][word]["vector"])
                    f.writelines("{}. Substring: {}, URLCount: {}, DocCount: {}, AVG URL DIST: {}, AVG DOC DIST: {}, TFIDF VECTOR: {} \n".format(count,word,urlcount,doccount,avgurldist,avgdocdist,vector))
                f.writelines("The average distance between substrings is {}\n".format(str(statistic["avg_distance"])))
                avg_distances.append(statistic["avg_distance"])
                f.writelines("The variance of the distance between substrings is {}\n".format(str(statistic["var_distance"])))
            #print(statistic["avg_distance"])
        plt.scatter(num_substrings,avg_distances)
        plt.show()
        f.close()'''