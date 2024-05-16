import sqlite3

conn = sqlite3.connect('orders.db', check_same_thread=False)
cur = conn.cursor()


def check_user(message):
    cur.execute('SELECT reg_id FROM users WHERE tg_id=?', (message.chat.id,))
    reg_id = int(cur.fetchone()[0])
    if reg_id:
        return reg_id
    else:
        return False


def check_passwd(message):
    cur.execute('SELECT reg_id FROM reg_data WHERE pass=?', (message.text,))
    reg_id = int(cur.fetchone()[0])
    #print(reg_id)
    if reg_id:
        return True
    else:
        return False


def add_user(message):
    cur.execute('SELECT reg_id FROM reg_data WHERE pass=?', (message.text,))
    reg_id = int(cur.fetchone()[0])
    #print(reg_id)
    cur.execute('INSERT INTO users VALUES(?, ?, ?);',(message.chat.id, reg_id, 1,))
    conn.commit()
    #cur.execute('INSERT INTO users VALUES(?, ?, ?, ?)',() )


def add_task_db(task_name, task_text, reg_id):
    cur.execute('INSERT INTO tasks (task_name, task_text, reg_id) VALUES(?, ?, ?);', (task_name.text, task_text.text, reg_id,))
    conn.commit()
    cur.execute('SELECT task_id FROM tasks WHERE task_name=? AND reg_id=?', (task_name.text, reg_id,))
    return cur.fetchone()[0]


def check_task_db(message):
    cur.execute('SELECT reg_id FROM users WHERE tg_id=?', (message.chat.id,))
    reg_id = int(cur.fetchone()[0])
    cur.execute('SELECT task_id, task_name FROM tasks WHERE reg_id=?', (reg_id,))
    return cur.fetchall()


def del_task_num_db(task_id, reg_id):
    cur.execute('SELECT * FROM tasks WHERE reg_id=? AND task_id=?', (reg_id, task_id,))
    if int(cur.fetchone()[0]):
        cur.execute('DELETE FROM tasks WHERE task_id=?', (task_id,))
        conn.commit()


