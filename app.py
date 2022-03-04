import flask
from flask import request, json, jsonify
import os
import time
from flask_cors import CORS
from flask_cors import cross_origin
import requests
import sqlite3
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from database_access import *


jwt =JWTManager()

app = flask.Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'udtsyngbdytsfg'
jwt.init_app(app)

CORS(app, cors_allowed_origins='*',support_credentials=True)

# api_url_base = "https://ntuttimetableapi.herokuapp.com/"
api_url_base = "http://localhost:5000/"

@app.route('/', methods=['GET'])
def home():
    return "{flag:this_is_not_a_flag}"

@app.route('/get_sem_info', methods=['POST'])
@cross_origin()
def get_sem_info():
    api_url = api_url_base+"get_semesters_info"
    try:
        content = request.get_json()
        uid = content["uid"]
        password = content["password"]
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})
    
    ac_data = jsonify({"uid":uid,"password":password})
    response = requests.post(api_url,json = {"uid":uid,"password":password})

    sem_info = response.text
    token_data = {"uid":uid}
    access_token = create_access_token(identity=token_data)
    return jsonify({'token':access_token,'sem_info':sem_info})

@app.route('/comment/add', methods=['POST'])
@cross_origin()
@jwt_required
def comment_add():
    try:
        content = request.get_json()
        data = content["data"]
        current_user = get_jwt_identity()
    except Exception as e:
        print(e)
        return jsonify({"status":"failure","reason":"invalid_request"})
    result = add_comment(data,current_user['uid'])
    return_data = jsonify({"status":result})
    return return_data

@app.route('/database/init', methods=['GET'])
@cross_origin()
@jwt_required
def database_init():
    init_database()
    return jsonify({"status":"success"})

if __name__ == '__main__':

    app.debug=True
    app.run(host="0.0.0.0", port=8080)

