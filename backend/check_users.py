import sqlite3
conn = sqlite3.connect('instance/vanmoly_v3.db')
cursor = conn.cursor()
cursor.execute("SELECT id, username, nickname, password_hash FROM users_v2")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}, Nickname: {row[2]}, Password Hash: {row[3]}")
conn.close()
