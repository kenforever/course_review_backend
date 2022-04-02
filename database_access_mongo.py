import pymongo
from uuid import uuid4
from bson.binary import UuidRepresentation
import time
import uuid
from bson.objectid import ObjectId

# Database(mongo) structure
#   comments
#   comment text NOT NULL | uid text NOT NULL | timestamp text NOT NULL | professer text NOT NULL | course_code text NOT NULL | rating integer NOT NULL 
#   log
#   action text NOT NULL | operator text NOT NULL | timestamp text NOT NULL | now text | before text
#   admin
#   uid text NOT NULL
#   uid_db
#   uid text NOT NULL  | uuid text NOT NULL

def add_comment(comment,uid,professer,course_code,rating):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        timestamp = time.time()
        db = client.comments
        collection = db.comments
        duplicate_data = list(collection.find({"professer":professer,"course_code":course_code,"uid":uid}))
        if len(duplicate_data) != 0:
            return("duplicate")

        comments_id = collection.insert_one({"comment":comment,"uid":uid,"timestamp":timestamp,"professer":professer,"course_code":course_code,"rating":rating})
        change = {"comment":comment,"comments_id":str(comments_id.inserted_id)}
        log_action("add_comment",uid,change)
        return("success")
    except Exception as e:
        print(e)
        return(str(e))

def del_comment(comment_id,operator):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.comments
        collection = db.comments
        comment = None
        comment_id = ObjectId(comment_id)
        comment = list(collection.find({"_id":comment_id},{"comment":1}))

        if len(comment) == 0:
            return("Comment_not_found")
        comment = comment[0]["comment"]

        collection.delete_one({"_id":comment_id})
        change_log = {"comment_id":comment_id,"comment":comment}
        log_action("del_comments",operator,change_log)
        return("success")
    except Exception as e:
        print(e)
        return(str(e))

def get_comment(type,target):
# get_comments can support three types of target:
#   course_code
#   uid
#   operator
#   comment_id
# please note that this will return all the comments in the database

    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.comments
        collection = db.comments

        if type == "course_code":
            result = list(collection.find({"course_code":target}))

        elif type == "uid":
            result = list(collection.find({"uid":target}))

        elif type == "professer":
            result = list(collection.find({"professer":target}))

        elif type == "comment_id":
            result = list(collection.find({"_id":ObjectId(target)}))

        else:
            return("failure")

        if len(list(result)) == 0:
            return("empty")
        
        for comment in result:
            comment_id = comment.pop("_id")
            comment["comment_id"] = str(comment_id)
        
        return(result)
    except Exception as e:
        print(e)
        return(str(e))

def edit_comment(comment_id,new_rating,new_comment,operator):
# id contain at comments return from get_comments
# update_dict should only contain rating and comment 
#
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.comments
        collection = db.comments

        comment_id = ObjectId(comment_id)
        comment = list(collection.find({"_id":comment_id},{"comment":1,"rating":1}))
        if len(comment) == 0:
            return("Comment_not_found")
        comment = comment[0]
        old_comment = comment["comment"]
        old_rating = comment["rating"]

        collection.update_one({"_id":comment_id},{"$set":{"comment":new_comment,"rating":new_rating}})
        change_log = {
            "comment_id":comment_id,
            "old":{
                "comment":old_comment,
                "rating":old_rating
            },
            "new":{
                "comment":new_comment,
                "rating":new_rating
            }
        }
        log_action("edit_comment",operator,change_log)
        return("success")

    except Exception as e:
        print(e)
        return(str(e))

def log_action(action,operator,change):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.comments
        collection = db.log

        collection.insert_one({"action":action,"operator":operator,"timestamp":time.time(),"change":change})
        return("success")
    except Exception as e:
        print(e)
        return(str(e))

def add_admin(uid,operator):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.comments
        collection = db.admin

        collection.insert_one({"uid":uid})
        return("success")
    except Exception as e:
        print(e)
        return(str(e))

def uuid_referer(target):
# target can be a uid or a uuid
# this function will return a uuid if target is a uid
# this function will return a uid if target is a uuid

    user_uuid = None
    user_uid = None
    result = None
    try:
        user_uuid = uuid.UUID(target)
    except ValueError:
        pass
    if user_uuid == None:
        user_uid = str(target)

    client = pymongo.MongoClient("mongodb://localhost:27017/",uuidRepresentation='standard')
    db = client.comments
    collection = db.uuid_db

    if user_uuid != None:
        result = list(collection.find({"uuid":user_uuid}))
        return result[0]["uid"]
    if user_uid != None:
        result = list(collection.find({"uid":user_uid},{"uuid":1}))
    if result == None or  len(list(result)) == 0 :
        new_uuid = uuid4()
        collection.insert_one({"uid":user_uid,"uuid":new_uuid})
        return(new_uuid)
    return str(result[0]["uuid"])
    

    
    