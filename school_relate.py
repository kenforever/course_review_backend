import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from unicodedata import normalize
import json
import math
import re


def get_semesters_info(uid,password):

    session = requests.Session()
    headers = {"referer":"https://nportal.ntut.edu.tw/index.do"} 
    ac = {'muid':uid, 'mpassword':password}
    response = session.post('https://nportal.ntut.edu.tw/login.do',data = ac, headers=headers)
    # try:
    #     fail = response.text
    #     soup = bs(fail,"html.parser")
    #     h3 = str(soup.find_all('h3')).split(">")[1].split("<")[0]
    #     if h3 == "登入失敗":
    #         return {"status":"failure","reason":"wrong_password"}
    # except:
    #     pass
    Cookies = session.cookies.get_dict()

    session = requests.Session()
    response = session.get('https://nportal.ntut.edu.tw/ssoIndex.do?apUrl=https://aps.ntut.edu.tw/course/tw/courseSID.jsp&apOu=aa_0010-&sso=true',cookies=Cookies)
    soup = bs(response.text,"html.parser")
    value = soup.find('input', {'name': 'sessionId'}).get('value')

    response = session.get('https://aps.ntut.edu.tw/course/tw/courseSID.jsp?sessionId='+value+'&reqFrom=Portal&userid='+uid+'&userType=50')
    TCookie = session.cookies.get_dict()

    response = session.get('https://aps.ntut.edu.tw/course/tw/Select.jsp?format=-3&code='+uid,cookies = TCookie)
    TCookie = session.cookies.get_dict()

    soup = bs(response.text,"html.parser")

    table = soup.find_all('table')
    df = pd.read_html(str(table[0]))

    data = str(pd.DataFrame(df[0])).split("\n")[1:]

    semesters = []
    for row in data:
        row = row.split(" ")
        year = row[2]
        sem = row[-2]
        semester = [year,sem]
        semesters.append(semester)
    
    aps_cookies = str(TCookie)
    
    result = {"semesters":semesters,"aps_cookies":aps_cookies}
        
    return result

def to_dict(day,target):
    day_list = {}
    for i in range(len(day)):
        day_temp = day[i]
        classroom = []
        professors = []
        try:
            math.isnan(day_temp)
            day_list[i+1] = "empty"
        except:
            course_temp = day[i].split(" ")
            course_name = course_temp[0]
            if len(course_temp) == 1 or course_name == "班週會及導師時間":
                pass
            elif len(course_temp) == 2:
                if bool(re.search(r'\d',course_temp[1])):
                    classroom.append(course_temp[1])
                else:
                    professors.append(course_temp[1])
            else:
                classroom.append(course_temp[-1])
                for professor in course_temp[1:-1]:
                    professors.append(professor)

            day_list_temp = {
                "course_name": course_name,
                "professor": professors,
                "classroom": classroom,
                "code": get_course_code(course_name,target)
            }
            day_list[i+1] = day_list_temp
    return day_list

def get_course_code(name,target):

    if name == "班週會及導師時間":
        return ""

    with open("./temps/"+target+"_code","r") as f:
        lines = f.readlines()
    for line in range(len(lines)):
        if name in lines[line]:
            code = lines[line-1].split(";")[1].split("\"")[0].split("=")[1]
            break
    return code

def Exchange(target,year,sem):
    with open("./temps/"+target,"r") as f:
        lines = f.readlines()
    with open("./temps/"+target,"w") as f:
        for line in lines:
            if line.startswith("<tr><td align=\"center\" colspan=\"6\">") == False:
                f.write(line)

    table_MN = pd.read_html("./temps/"+target,encoding='utf-8')
    table_dataframe = pd.DataFrame(table_MN[0])

    mon = to_dict(table_dataframe["一"].tolist(),target)
    tue = to_dict(table_dataframe["二"].tolist(),target)
    wed = to_dict(table_dataframe["三"].tolist(),target)
    thu = to_dict(table_dataframe["四"].tolist(),target)
    fri = to_dict(table_dataframe["五"].tolist(),target)
    try:
        sat = to_dict(table_dataframe["六"].tolist())
    except:
        sat = {}
    
    info = {
        "target":target,
        "year":year,
        "sem":sem
    }

    total_list = {
        "mon": mon,
        "tue": tue,
        "wed": wed,
        "thu": thu,
        "fri": fri,
        "sat": sat,
        "info":info
    }
    
    return total_list

def file_create(cookie,year,sem,target):
    
    session = requests.Session()
    TCookie = cookie

    response = session.get('https://aps.ntut.edu.tw/course/tw/Select.jsp?format=-2&code='+target+"&year="+year+"&sem="+sem,cookies = TCookie)
    TCookie = session.cookies.get_dict()

    soup = bs(response.text,"html.parser")
    table = soup.find_all('table')
    
    with open("./temps/"+target,"w",encoding='utf-8') as f :
        f.write(str(table[0]))

    with open("./temps/"+target+"_code","w",encoding='utf-8') as f :
        f.write(str(table[1]))

def courses_studied(uid,cookie,year,sem):
    file_create(cookie,year,sem,uid)
    data = Exchange(uid,year,sem)
    course_code = []
    for i in range(1,12):
        if data["mon"][i] != "empty":
            course_code.append(data["mon"][i]["code"])
        if data["tue"][i] != "empty":
            course_code.append(data["tue"][i]["code"])
        if data["wed"][i] != "empty":
            course_code.append(data["wed"][i]["code"])
        if data["thu"][i] != "empty":
            course_code.append(data["thu"][i]["code"])
        if data["fri"][i] != "empty":
            course_code.append(data["fri"][i]["code"])
        if data["sat"]!={}:
            if data["sat"][i] != "empty":
                course_code.append(data["sat"][i]["code"])
    course_code = list(dict.fromkeys(course_code))
    return course_code

def course_studied_check(uid,course_code,sem,aps_cookies,year):
    courses_studied_codes = courses_studied(uid,aps_cookies,year,sem)
    if course_code in courses_studied_codes:
        return True
    else:
        return False
