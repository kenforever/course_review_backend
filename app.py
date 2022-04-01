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
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
import base64
import json
from database_access import *
import jwt as PyJWT
from init import *
from get_semesters_info import *
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
@jwt_refresh_token_required
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
        sem_info = get_semesters_info(uid,password,uid)
        print(sem_info)
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"cant_get_info"})

    try:
        if sem_info["status"] == "failure":
            return jsonify(sem_info)
    except:
        pass

    token_data = {"uid":uid}
    access_token = create_access_token(identity=token_data)
    refresh_token = create_refresh_token(identity=token_data)
    return jsonify({"status":"success",'access_token':access_token,'sem_info':sem_info,'refresh_token':refresh_token})

@app.route('/comment/add', methods=['POST'])
@cross_origin()
@jwt_required
def comment_add():
    try:
        content = request.get_json()
        comment = content["comment"]
        uid = get_jwt_identity()["uid"]
        professer = content["professer"]
        course_code = content["course_code"]
        rating = content["rating"]
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})

    if rating > 5 or rating < 0:
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
@jwt_required
def comment_get():
    try:
        content = request.get_json()
        type = content["type"]
        if type == "course_code":
            course_code = content["target"]
            result = get_comments_by_course_code(course_code)
        elif type == "professer":
            professer = content["target"]
            result = get_comments_by_professer(professer)
        elif type == "uid":
            uid = content["target"]
            result = get_comments_by_uid(uid)
        else:
            result = "type_not_support"
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":str(e)})
    return_data = jsonify({"status":"success","result":result})
    return return_data

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

if __name__ == '__main__':

    app.debug=True
    app.run(host="0.0.0.0", port=8080)

