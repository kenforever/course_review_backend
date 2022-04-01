import sqlite3
import requests
import FileCreate
from school_relate import courses_studied

def admin_check(uid):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE uid=?",(uid,))
    data = c.fetchone()
    conn.close()
    if data:
        return True
    else:
        return False

def course_studied_check(uid,course_code,sem,aps_cookies,year):
    courses_studied_codes = courses_studied(uid,aps_cookies,year,sem)
    if course_code in courses_studied_codes:
        return True
    else:
        return False
