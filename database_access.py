import sqlite3
from datetime import datetime

def init_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comment
                 (comment text, add_user text, add_time text)''')
    conn.commit()
    conn.close()
    return("finish")

def add_comment(data,user):
    try:
        conn = sqlite3.connect('database.db')
        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")
        c = conn.cursor()
        # check if the data is already in the database
        c.execute("SELECT * FROM comment WHERE comment=?",(data,))
        if c.fetchone() is None:
            c.execute("INSERT INTO comment VALUES (?,?,?)",(data,user,now))
            conn.commit()
            conn.close()
            return("add_success")
        else:
            conn.close()
            return("commit exist")
    except Exception as e:
        print(e)
        conn.close()
        return(e)