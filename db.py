import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["vscribe"]
mycol = mydb["qna"]
# mydict = { "qno" : "3", "question" : "Tomato is a fruit ", "answer" : "", "option1" : "True", "option2" : "False" }
# x = mycol.insert_one(mydict)

mydoc = mycol.find()
for i in mydoc:
    print(i)

# myquery = { "qno": "1" }
# newvalues = { "$set": { "answer": "" } }
# mycol.update_one(myquery, newvalues)

# myquery = { "qno": "2" }
# newvalues = { "$set": { "answer": "" } }
# mycol.update_one(myquery, newvalues)

# myquery = { "qno": "3" }
# newvalues = { "$set": { "answer": "" } }
# mycol.update_one(myquery, newvalues)