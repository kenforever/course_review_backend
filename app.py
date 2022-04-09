from hashlib import algorithms_available
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from database_access import uuid_referer
from school_relate import *
from database_access import *
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from enum import Enum
import os
from dotenv import load_dotenv

def load_env(IS_HEROKU: bool):
    if not IS_HEROKU:
        load_dotenv()
    try:
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM")
        ACCESS_TOKEN_EXPIRE_MINUTES = eval(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        print("setting up...")
        print("set secret key as ", SECRET_KEY)
        print("set algorithm as ", ALGORITHM)
        print("set access token expire minutes as ", ACCESS_TOKEN_EXPIRE_MINUTES)
        print("set mongodb url as ", os.getenv("MONGODB_URL"))
        os.mkdir("./temps")
    except Exception as e:
        print(e)

IS_HEROKU = os.getenv("IS_HEROKU")
load_env(IS_HEROKU)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_sem_info")

class Search_Type(str, Enum):
    course_code = "course_code"
    uid = "uid"
    professer = "professer"
    comment_id = "comment_id"

class Action(str, Enum):
    delete = "delete"
    edit = "edit"

class Comment_Add(BaseModel):
    comment: str
    rating: float
    professer: str
    course_code: str

class Comment_Edit(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Sem_Info(BaseModel):
    access_token: str
    token_type: str
    sem_info: dict

class Comment_Get(BaseModel):
    status: str
    result: dict

class Course_Check_Data(BaseModel):
    course_code: str
    year: str
    sem: str

@app.get("/comment/get/{comment_id}", response_model=Comment_Get)
def get_comment(comment_id: str):
    try:
        result = get_comment_by_id(comment_id)
    except Exception as e:
        print(e)
        return {"status":"failure","reason":str(e)}
    if result == "failure":
        return {"status":"failure","reason":"cant_get_comment"}
    return {"status":"success","result":result}

@app.post("/comment/search/{type}")
def search_comment_by_type(type: Search_Type, target: str,token: str = Depends(oauth2_scheme)):
    result = search_comment(type,target)
    if result == "failure":
        return {"status":"failure","reason":"cant_search_comments"}
    return {"status":"success","result":result}

@app.post("/comment/add")
def add_comment_api(comment_data: Comment_Add, token: str = Depends(oauth2_scheme)):
    try:
        uid = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["uuid"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    comment_data = comment_data.dict()
    comment = comment_data["comment"]
    rating = comment_data["rating"]
    professer = comment_data["professer"]
    course_code = comment_data["course_code"]

    if type(rating) == int or type(rating) == float:
        if rating > 5 or rating < 0:
            return {"status":"failure","reason":"invalid_rating"}
    else:
        return {"status":"failure","reason":"invalid_rating"}
    
    try:
        result = add_comment(comment=comment, uid=uid, rating=rating, professer=professer, course_code=course_code)
    except Exception as e:
        print(e)
        return {"status":"failure","reason":str(e)}
    if result == "failure":
        return {"status":"failure","reason":"internal_error"}
    return(result)

@app.delete("/comment/{comment_id}")
def del_comment_api(comment_id: str, token: str = Depends(oauth2_scheme)):
    try:
        uid = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["uuid"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        comment = get_comment_by_id(comment_id)
        comment_owner = comment["uid"]
    except Exception as e:
        print(e)
        return {"status":"failure","reason":str(e)}
    if comment_owner != uid:
        return {"status":"failure","reason":"can_not_delete_others_comment"}
    result = del_comment(comment_id, uid)
    if result == "success":
        return {"status":"success"}
    else:
        return {"status":"failure","reason":result}

@app.post("/comment/edit/{comment_id}")
def edit_comment_api(comment_id: str, data: Comment_Edit, token: str = Depends(oauth2_scheme)):
    try:
        uid = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["uuid"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = data.dict()

    try:
        comment = get_comment_by_id(comment_id)
        comment_owner = comment["uid"]
    except Exception as e:
        print(e)
        return {"status":"failure","reason":str(e)}
    if comment_owner != uid:
        return {"status":"failure","reason":"can_not_delete_others_comment"}

    if type(data["rating"]) == int or type(data["rating"]) == float:
        if data["rating"] > 5 or data["rating"] < 0:
            return {"status":"failure","reason":"invalid_rating"}
    else:
        return {"status":"failure","reason":"invalid_rating"}
    
    result = edit_comment(comment_id, data["rating"], data["comment"], uid)
    if result == "success":
        return {"status":"success"}
    else:
        return {"status":"failure","reason":result}

@app.post("/course/check")
def check_course_api(target_data: Course_Check_Data, token: str = Depends(oauth2_scheme)):
    try:
        uid = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["uuid"]
        aps_cookies = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["aps_cookies"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    target_data = target_data.dict()
    course_code = target_data["course_code"]
    uid = uuid_referer(uid)
    year = target_data["year"]
    sem = target_data["sem"]
    result = course_studied_check(uid,course_code,sem,aps_cookies,year)

    return {"status":"success","result":result}


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/get_sem_info", response_model=Sem_Info)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    uid = form_data.username
    password = form_data.password
    sem_info = get_semesters_info(uid,password)
    print(sem_info)
    try:
        if sem_info["status"] == "failure":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        print(e)
        pass
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    user_uuid = uuid_referer(uid)
    access_token = create_access_token(
        data={"uuid": user_uuid,"aps_cookies":sem_info["aps_cookies"]}, expires_delta=access_token_expires
    )
    sem_info.pop("aps_cookies")
    return_data = {"access_token": access_token, "token_type":"bearer","sem_info": sem_info}
    print(return_data)
    return return_data

@app.post("/refresh", response_model=Token)
def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    uid = payload["uid"]
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"uid": uid}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type":"bearer"}
