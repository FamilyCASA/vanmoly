import hashlib, sqlite3, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# 计算 van654321 的hash
pw = 'van654321'
h = hashlib.sha256(pw.encode()).hexdigest()
print('van654321 hash:', h)

conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
conn.text_factory = str
cur = conn.cursor()

# 检查users_v2表admin
try:
    cur.execute("SELECT id, username, nickname, phone, password_hash, status FROM users_v2 WHERE username='admin' LIMIT 1")
    row = cur.fetchone()
    if row:
        print('users_v2 admin:', row)
        print('stored hash:', row[4])
        print('hash matches van654321:', row[4] == h)
    else:
        print('No admin in users_v2')
except Exception as e:
    print('users_v2 query error:', e)

conn.close()