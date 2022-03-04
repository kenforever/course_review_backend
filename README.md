# 北科課程好朋友評論系統後端

## 安裝 installation

在 config.json 填入相對應資料後，安裝所需需求。
fill in config.json and install requirements.

` pip install -r requirements.txt`

run app.py using flask


## 開始使用 usage

### /init

初始化資料庫

initialize database

```
curl --location --request GET '127.0.0.1:8080/init_db' \
--header 'Authorization: Bearer {access_token}'
```

response

```
{
    "status": "database_init_success"
}
```


### /get_sem_info

取得所有在學學年與學期，同時作為登入並取得權杖用

Get all avaliable school years and semesters, use to login and get token at the same time.

```
curl --location --request POST '{api_url}/get_sem_info' \
--header 'Content-Type: application/json' \
--data '{"uid":{student_ID},
"password":{password_of_your_school_portal}'
```

參數 Parameter   |形態 type   |解釋 explanation
-----------------|------------|---------------
uid              |text        |學號 student ID
password         |text        |入口密碼 password for portal

response

```
{
  "access_token": {access_token},
  "refresh_token": {refresh_token},
  "sem_info": [
    [
      "110",
      "2"
    ],
    [
      "110",
      "1"
    ],
    [
      "109",
      "2"
    ],
    [
      "109",
      "1"
    ]
  ],
  "status": "success"
}
```

### /comment/add

新增一則留言到資料庫

add one comment to database

```
curl --location --request POST '{api_url}/comment/add' \
--header 'Authorization: Bearer {access_token}' \
--header 'Content-Type: application/json' \
--data '{
    "comment":{comment},
    "professer":{professer},
    "course_code":{course_code},
    "rating":{rating_for_this_course}
}'
```

參數 Parameter   |形態 type   |解釋 explanation
-----------------|------------|---------------
comment          |text        |評論內容 comment content
professer        |text        |教授名稱 professer name
course_code      |text        |課程代碼 code for course
rating           |text        |評價分數 rating score

response

```
{
    "status": "success"
}
```

### /comment/get

允許以不同方法取得評論，包括以課程代號，教授名稱，學號。

Allow getting comment from different method, inclouding course code, professer name, student ID.

```
curl --location --request POST '{api_url}/comment/get' \
--header 'Authorization: Bearer {access_token}' \
--header 'Content-Type: application/json' \
--data-raw '{
    "type":{type},
    "target":{search_target}
}'
```

參數 Parameter   |形態 type   |解釋 explanation
-----------------|------------|---------------
type             |text        |種類 type you want to search
target           |text        |要尋找的對象 your search target

response
```
{
    "result": [
        {
            "comment": "SUfsdfS",
            "course_code": "12312342423",
            "professer": "SUCsdfsdfKS",
            "rating": 3,
            "timestamp": "1646409744.84242",
            "uid": "109AB0057"
        },
        {
            "comment": "SUfsdffffS",
            "course_code": "123123424fff23",
            "professer": "SUCsdfsfffdfKS",
            "rating": 3,
            "timestamp": "1646409766.5835",
            "uid": "109AB0057"
        }
    ],
    "status": "success"
}
```

### /refresh

使用刷新權杖取得新的權限權杖

get new access token using refresh token

```
curl --location --request POST '{api_url}/refresh' \
--header 'Authorization: Bearer {refresh_token}'
```

response

```
{
    "access_token": "{access_token}"
}
```
