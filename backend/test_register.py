import sqlite3, requests, json

# 验证列是否存在
conn = sqlite3.connect(r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(customer)')
cols = [row[1] for row in cursor.fetchall()]
print('Customer columns:', cols)
print('password_hash exists:', 'password_hash' in cols)

# 测试注册
r = requests.post('http://localhost:8080/api/v3/customer/register',
    json={'nickname': '测试用户2', 'phone': '13900001112', 'password': 'test123'})
print(f'Register status: {r.status_code}')
print(f'Response: {r.text[:300]}')

# 检查手机号是否已写入
cursor.execute('SELECT id, name, phone, password_hash FROM customer WHERE phone IN ("13800138002", "13800138003", "13900001112")')
print('写入的客户:', cursor.fetchall())
