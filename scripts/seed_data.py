"""
为D&B 帝标|设记家系统生成示例数据
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'

def seed_customers(conn):
    cursor = conn.cursor()
    customers = [
        ('张三', '13800138001', '男', 'zhangsan', '万科城', '三室两厅', 120, '20-30万', '已接触', '待跟进', '线上咨询', '现代简约'),
        ('李四', '13800138002', '女', 'lisi', '碧桂园', '四室两厅', 150, '30-50万', '意向客户', '跟进中', '自然进店', '北欧风格'),
        ('王五', '13800138003', '男', 'wangwu', '恒大绿洲', '两室一厅', 90, '10-20万', '签约客户', '已签约', '老客户推荐', '中式风格'),
        ('赵六', '13800138004', '女', 'zhaoliu', '保利花园', '三室两厅', 130, '30-50万', '潜在客户', '待跟进', '楼盘合作', '轻奢风格'),
        ('钱七', '13800138005', '男', 'qianqi', '龙湖天街', '四室两厅', 180, '50万以上', '老客户', '已完成', '线上咨询', '现代简约'),
    ]
    
    for name, phone, gender, wechat, building, house_type, area, budget, ctype, status, source, style in customers:
        cursor.execute("""
            INSERT OR IGNORE INTO customer (name, phone, gender, wechat, building_name, house_type, house_area, 
                budget, customer_type, status, source, style_preference, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (name, phone, gender, wechat, building, house_type, area, budget, ctype, status, source, style,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  客户: {len(customers)}条')

def seed_employees(conn):
    cursor = conn.cursor()
    employees = [
        ('admin', '管理员', 'admin@vanmoly.com', '13800000001', 'admin', '在职'),
        ('sales1', '张销售', 'sales1@vanmoly.com', '13800000002', 'sales', '在职'),
        ('sales2', '李销售', 'sales2@vanmoly.com', '13800000003', 'sales', '在职'),
        ('design1', '王设计', 'design1@vanmoly.com', '13800000004', 'designer', '在职'),
        ('design2', '赵设计', 'design2@vanmoly.com', '13800000005', 'designer', '在职'),
    ]
    
    for username, name, email, phone, role, status in employees:
        cursor.execute("""
            INSERT OR IGNORE INTO employee (username, name, email, phone, role, 
                status, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (username, name, email, phone, role, status,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  员工: {len(employees)}条')

def seed_buildings(conn):
    cursor = conn.cursor()
    buildings = [
        ('万科城', '成都市高新区天府大道', '住宅', '万科地产', '万科物业', '合作中', '独家'),
        ('碧桂园', '成都市天府新区华阳', '住宅', '碧桂园集团', '碧桂园物业', '合作中', '优先'),
        ('恒大绿洲', '成都市龙泉驿区大面', '住宅', '恒大集团', '恒大物业', '洽谈中', '普通'),
        ('保利花园', '成都市武侯区簇桥', '住宅', '保利地产', '保利物业', '合作中', '独家'),
        ('龙湖天街', '成都市锦江区春熙路', '商业', '龙湖集团', '龙湖物业', '合作中', '优先'),
    ]
    
    for name, address, ptype, developer, property_co, coop_status, coop_type in buildings:
        cursor.execute("""
            INSERT OR IGNORE INTO building (name, address, property_type, developer, property_company,
                cooperation_status, cooperation_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, address, ptype, developer, property_co, coop_status, coop_type,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  楼盘: {len(buildings)}条')

def seed_contracts(conn):
    cursor = conn.cursor()
    contracts = [
        ('C2024001', 1, 1, 150000, '进行中', '2024-01-15'),
        ('C2024002', 2, 2, 280000, '进行中', '2024-02-20'),
        ('C2024003', 3, 3, 95000, '已完成', '2024-03-10'),
    ]
    
    for code, customer_id, creator_id, amount, status, sign_date in contracts:
        cursor.execute("""
            INSERT OR IGNORE INTO contract (contract_no, customer_id, creator_id, total_amount, 
                status, signed_date, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (code, customer_id, creator_id, amount, status, sign_date,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  合同: {len(contracts)}条')

def seed_quotes(conn):
    cursor = conn.cursor()
    quotes = [
        ('Q2024001', 1, 1, 120000, '已确认'),
        ('Q2024002', 2, 2, 250000, '待确认'),
        ('Q2024003', 3, 1, 85000, '草稿'),
    ]
    
    for code, customer_id, creator_id, total, status in quotes:
        cursor.execute("""
            INSERT OR IGNORE INTO quote (quote_no, customer_id, creator_id, total_amount, 
                status, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (code, customer_id, creator_id, total, status,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  报价: {len(quotes)}条')

def seed_schemes(conn):
    cursor = conn.cursor()
    schemes = [
        ('SC2024001', 1, '张三', '13800138001', '张三-现代简约方案', '现代简约', '120', '待提交'),
        ('SC2024002', 2, '李四', '13800138002', '李四-北欧风格方案', '北欧风格', '150', '待提交'),
    ]
    
    for code, customer_id, customer_name, customer_phone, name, style, area, status in schemes:
        cursor.execute("""
            INSERT OR IGNORE INTO customer_schemes (scheme_no, customer_id, customer_name, customer_phone,
                name, style, area, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, customer_id, customer_name, customer_phone, name, style, area, status,
              datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    print(f'  方案: {len(schemes)}条')

if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    print('开始生成示例数据...')
    seed_customers(conn)
    seed_employees(conn)
    seed_buildings(conn)
    seed_contracts(conn)
    seed_quotes(conn)
    seed_schemes(conn)
    conn.close()
    print('完成!')
