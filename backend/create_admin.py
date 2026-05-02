import sqlite3
import hashlib
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('instance/vanmoly_v3.db')
cursor = conn.cursor()

# 生成密码哈希
password_hash = hashlib.sha256('Van9999'.encode()).hexdigest()
print(f"密码哈希: {password_hash}")

# 检查用户是否已存在
cursor.execute("SELECT id FROM users_v2 WHERE username = ?", ('vanmoly',))
existing = cursor.fetchone()

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if existing:
    # 更新现有用户
    cursor.execute("""
        UPDATE users_v2 
        SET password_hash = ?, 
            nickname = '超级管理员',
            role = 'super_admin',
            status = 'active',
            updated_at = ?
        WHERE username = ?
    """, (password_hash, now, 'vanmoly'))
    print("用户已更新")
else:
    # 创建新用户
    cursor.execute("""
        INSERT INTO users_v2 (username, nickname, password_hash, role, status, phone, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('vanmoly', '超级管理员', password_hash, 'super_admin', 'active', '13900139000', now, now))
    print("用户已创建")

# 提交更改
conn.commit()

# 验证
cursor.execute("SELECT id, username, nickname, role, password_hash FROM users_v2 WHERE username = ?", ('vanmoly',))
user = cursor.fetchone()
if user:
    print(f"\n用户信息:")
    print(f"ID: {user[0]}")
    print(f"用户名: {user[1]}")
    print(f"昵称: {user[2]}")
    print(f"角色: {user[3]}")
    print(f"密码哈希: {user[4]}")

conn.close()
print("\n完成！")
