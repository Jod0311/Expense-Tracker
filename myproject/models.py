import sqlite3
from user import User

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2])
    return None

def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2])
    return None

def insert_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def insert_expense(description, amount, date, user_id, category):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expense (description, amount, date, user_id, category) VALUES (?, ?, ?, ?, ?)', 
                   (description, amount, date, user_id, category))
    conn.commit()
    conn.close()

def get_expenses_by_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT description, amount, date, category FROM expense WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()
    conn.close()
    
    # Convert the list of tuples to a list of dictionaries
    expenses_dicts = []
    for expense in expenses:
        expenses_dicts.append({
            'description': expense[0],
            'amount': expense[1],
            'date': expense[2],
            'category': expense[3]
        })
    
    return expenses_dicts