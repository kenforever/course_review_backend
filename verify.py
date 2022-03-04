import sqlite3

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