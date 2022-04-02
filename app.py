import flask
from flask import request, json, jsonify
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_cors import CORS
from flask_cors import cross_origin
from uuid import uuid5
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity
)
import base64
import json
import jwt as PyJWT
from init import *
from school_relate import *
from database_access_mongo import *
jwt =JWTManager()

with open("config.json", "r") as f:
    config = json.load(f)
    JWT_SECRET_KEY = config["JWT_SECRET_KEY"]

app = flask.Flask(__name__)

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=10)

jwt.init_app(app)

CORS(app, cors_allowed_origins='*',support_credentials=True)

@app.route('/', methods=['GET'])
def home():
    return "{flag:this_is_not_a_flag}"

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@app.route('/get_sem_info', methods=['POST'])
@cross_origin()
def get_sem_info():
    try:
        content = request.get_json()
        uid = content["uid"]
        password = content["password"]
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})
    
    try:
        print(uid,password)
        sem_info = get_semesters_info(uid,password)
        print(sem_info)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_get_info"})

    try:
        if sem_info["status"] == "failure":
            return jsonify(sem_info)
    except:
        pass

    user_uuid = uuid_referer(uid)
    token_data = {"uid":user_uuid}
    access_token = create_access_token(identity=token_data)
    refresh_token = create_refresh_token(identity=token_data)
    return jsonify({"status":"success",'access_token':access_token,'sem_info':sem_info,'refresh_token':refresh_token})

@app.route('/comment/add', methods=['POST'])
@cross_origin()
@jwt_required()
def comment_add():
    try:
        content = request.get_json()
        comment = content["comment"]
        uid = get_jwt_identity()["uid"]
        professer = content["professer"]
        course_code = content["course_code"]
        rating = eval(str(content["rating"]))
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})

    if type(rating) == int or type(rating) == float:
        if rating > 5 or rating < 0:
            return jsonify({"status":"failure","reason":"invalid_rating"})
    else:
        return jsonify({"status":"failure","reason":"invalid_rating"})


    try:    
        result = add_comment(comment,uid,professer,course_code,rating)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_insert"})

    if result == "success": 
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failure","reason":result})


@app.route('/comment/get', methods=['POST'])
@cross_origin()
@jwt_required()
def comments_get():
    try:
        content = request.get_json()
        type = content["type"]
        if type == "course_code":
            course_code = content["target"]
            result = get_comment("course_code",course_code)
        elif type == "professer":
            professer = content["target"]
            result = get_comment("professer",professer)
        elif type == "uid":
            uid = content["target"]
            result = get_comment("uid",uid)
        else:
            result = "type_not_support"
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":str(e)})
    if result == "failure":
        return jsonify({"status":"failure","reason":"cant_get_comments"})
    return_data = jsonify({"status":"success","result":result})
    return return_data

@app.route('/comment/delete', methods=['POST'])
@cross_origin()
@jwt_required()
def comment_delete():
    try:
        content = request.get_json()
        comment_id = content["comment_id"]
        uid = get_jwt_identity()["uid"]
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})

    try:
        result = del_comment(comment_id,uid)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_delete"})

    if result == "success":
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failure","reason":result})

@app.route('/init', methods=['GET'])
def db_init():
    init = init_check()
    if init == "init_finished":
        print("already initialized")
    elif init == "not_init":
        print("start to initialize")
        initialization()
        print("initialization finished")
    else:
        print("initialize fail, reason: "+init)
        return jsonify({"status":"failure","reason":str(init)})
    
    return jsonify({"status":"init_finished"})

@app.route("/comment/edit", methods=["POST"])
@cross_origin()
@jwt_required()
def comment_edit():
    try:
        content = request.get_json()
        comment_id = content["comment_id"]
        comment = content["comment"]
        rating = content["rating"]
        uid = get_jwt_identity()["uid"]
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})

    try:
        result = edit_comment(comment_id,rating,comment,uid)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_edit"})

    if result == "success":
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failure","reason":result})

@app.route("/course/check", methods=["POST"])
@cross_origin()
@jwt_required()
def course_check():
    try:
        content = request.get_json()
        course_code = content["course_code"]
        sem = content["sem"]
        aps_cookies = content["aps_cookies"]
        year = content["year"]
        uid = uuid_referer(get_jwt_identity()["uid"])
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})

    try:
        result = course_studied_check(uid,course_code,sem,aps_cookies,year)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_check"})

    if result == "success":
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failure","reason":result})

if __name__ == '__main__':

    app.debug=True
    app.run(host="0.0.0.0", port=8080)

