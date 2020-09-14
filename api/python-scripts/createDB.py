from pymongo import MongoClient
import json

TRANSCRIPTS = "../data/video-transcripts/transcript_data.json"
mongoClient = MongoClient("mongodb://localhost:27017/")
db = mongoClient["tedtranscript"]

def createDB(tanscripts=TRANSCRIPTS):
    if "transcript" in db.list_collection_names():
        print('Warning: Collection "transcript" already exists')
        print("Do you want to overwrite the existing transcript collection (Y/N)")
        ans = input()
        ans = ans.lower()
        while ans != "y"  and ans != "n":
            print("Enter Y or N")
            ans = input()
        if ans == "n":
            print("Exitting....")
            return False
    transcript_collection = db["transcript"]
    with open(TRANSCRIPTS,'r', encoding = "utf8") as f:
        transcripts_json = json.load(f)
    transcript_collection.insert_many(transcripts_json)
    return True



if __name__ == "__main__":
    print("Creating transcript database....")
    createDB()
