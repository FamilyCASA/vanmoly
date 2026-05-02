import sqlite3

# 连接数据库
conn = sqlite3.connect('instance/vanmoly_v3.db')
cursor = conn.cursor()

# 更新手机号
cursor.execute("""
    UPDATE users_v2 
    SET phone = ?
    WHERE username = ?
""", ('13908179177', 'vanmoly'))

# 提交更改
conn.commit()

# 验证
cursor.execute("SELECT id, username, nickname, phone FROM users_v2 WHERE username = ?", ('vanmoly',))
user = cursor.fetchone()
if user:
    print(f"用户信息:")
    print(f"ID: {user[0]}")
    print(f"用户名: {user[1]}")
    print(f"昵称: {user[2]}")
    print(f"手机号: {user[3]}")

conn.close()
print("\n手机号已更新！")
