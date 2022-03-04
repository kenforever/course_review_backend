import sqlite3
from datetime import datetime
import time

# Database structure
#   main 
# comment text NOT NULL | uid text NOT NULL | timestamp text NOT NULL | professer text NOT NULL | course_code text NOT NULL | rating integer NOT NULL 
#   log 
# action text NOT NULL | operator text NOT NULL | timestamp text NOT NULL | now text | before text 
#   admin 
# uid text NOT NULL 

def init_database():
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS main
                    (comment text NOT NULL, uid text NOT NULL, timestamp text NOT NULL, professer text NOT NULL, course_code text NOT NULL, rating integer NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS log
                        (action text NOT NULL, operator text NOT NULL, timestamp text NOT NULL, now text, before text)''')

        c.execute('''CREATE TABLE IF NOT EXISTS admin
                        (uid text NOT NULL)''')

        conn.commit()
        conn.close()
        return("database_init_success")
    except Exception as e:
        print(e)
        return("failure")

def add_comment(comment,uid,professer,course_code,rating):
    try:
        conn = sqlite3.connect('./data/database.db')
        #now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")
        timestamp = time.time()
        c = conn.cursor()
        # check if the data is already in the database
        c.execute("SELECT * FROM main WHERE uid=? AND course_code=? AND professer=?",(uid,course_code,professer))
        result = c.fetchall()
        if len(result) == 0:
            c.execute("INSERT INTO main VALUES (?,?,?,?,?,?)",(comment,uid,timestamp,professer,course_code,rating))
            conn.commit()
            conn.close()
            log_action("add_comment",uid,comment,"")
            return("success")
        else:
            conn.close()
            return("duplicate")
    except Exception as e:
        print(e)
        return(e)

def get_comments_by_course_code(course_code):
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM main WHERE course_code=?",(course_code,))
        result = c.fetchall()
        conn.close()
        if result == []:
            return("empty")
        return(result)
    except Exception as e:
        print(e)
        return(e)

def get_comments_by_professer(professer):
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM main WHERE professer=?",(professer,))
        result = c.fetchall()
        conn.close()
        if result == []:
            return("empty")
        return(result)
    except Exception as e:
        print(e)
        return(e)

def get_comments_by_uid(uid):
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM main WHERE uid=?",(uid,))
        result = c.fetchall()
        conn.close()
        if result == []:
            return("empty")
        return_data = []
        for comment_data in result:
            comment = comment_data[0]
            uid = comment_data[1]
            timestamp = comment_data[2]
            professer = comment_data[3]
            course_code = comment_data[4]
            rating = comment_data[5]
            comment_data = {
                "comment":comment,
                "uid":uid,
                "timestamp":timestamp,
                "professer":professer,
                "course_code":course_code,
                "rating":rating
            }
            return_data.append(comment_data)

        return(return_data)
    except Exception as e:
        print(e)
        return(e)

def log_action(action,operator,now,before):
    try:
        timestamp = time.time()
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("INSERT INTO log VALUES (?,?,?,?,?)",(action,operator,timestamp,now,before))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return(e)

def get_log():
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM log")
        result = c.fetchall()
        conn.close()
        if result == []:
            return("empty")
        return(result)
    except Exception as e:
        print(e)
        return(e)

def add_admin(uid,operator):
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("INSERT INTO admin VALUES (?)",(uid,))
        conn.commit()
        conn.close()
        log = "add admin: "+uid
        log_action(log,operator,"","")
        return("success")
    except Exception as e:
        print(e)
        return(e)

def remove_admin(uid,operator):
    try:
        conn = sqlite3.connect('./data/database.db')
        c = conn.cursor()
        c.execute("DELETE FROM admin WHERE uid=?",(uid,))
        conn.commit()
        conn.close()
        log = "remove admin: "+uid
        log_action(log,operator,"","")
        return("success")
    except Exception as e:
        print(e)
        return(e)