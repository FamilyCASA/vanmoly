"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 完整API服务器
使用轻量级方式避免SIGKILL
"""
import os
import sys
import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vanmoly_v3.db')

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        try:
            # 根路由
            if path in ['/api/v3/', '/api/v3']:
                self.send_json({'code': 200, 'data': {'version': '3.0.8'}, 'message': 'OK'})
            elif path == '/api/v3/health':
                self.send_json({'code': 200, 'data': {'status': 'ok'}, 'message': 'OK'})
            
            # 物料模块
            elif path == '/api/v3/materials':
                self.send_json(self.get_materials(params))
            elif path == '/api/v3/materials/categories':
                self.send_json(self.get_categories())
            elif path == '/api/v3/materials/stats':
                self.send_json(self.get_stats())
            elif path == '/api/v3/materials/options':
                self.send_json(self.get_material_options())
            
            # 客户模块
            elif path == '/api/v3/customers':
                self.send_json(self.get_customers(params))
            elif path == '/api/v3/customers/stats':
                self.send_json(self.get_customer_stats())
            elif path == '/api/v3/customers/options':
                self.send_json(self.get_customer_options())
            
            # 员工模块
            elif path == '/api/v3/employees':
                self.send_json(self.get_employees(params))
            elif path == '/api/v3/employees/options':
                self.send_json(self.get_employee_options())
            
            # 合同模块
            elif path == '/api/v3/contracts':
                self.send_json(self.get_contracts(params))
            
            # 楼盘模块
            elif path == '/api/v3/buildings':
                self.send_json(self.get_buildings(params))
            
            # 报价模块
            elif path == '/api/v3/quotes':
                self.send_json(self.get_quotes(params))
            
            # 方案模块
            elif path == '/api/v3/schemes':
                self.send_json(self.get_schemes(params))
            
            else:
                self.send_json({'code': 404, 'message': 'Not found'}, 404)
        except Exception as e:
            self.send_json({'code': 500, 'message': str(e)}, 500)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            if path == '/api/v3/auth/login':
                self.send_json(self.auth_login(data))
            elif path == '/api/v3/customers':
                self.send_json(self.create_customer(data))
            elif path == '/api/v3/employees':
                self.send_json(self.create_employee(data))
            elif path == '/api/v3/contracts':
                self.send_json(self.create_contract(data))
            elif path == '/api/v3/buildings':
                self.send_json(self.create_building(data))
            elif path == '/api/v3/quotes':
                self.send_json(self.create_quote(data))
            elif path == '/api/v3/schemes':
                self.send_json(self.create_scheme(data))
            else:
                self.send_json({'code': 404, 'message': 'Not found'}, 404)
        except Exception as e:
            self.send_json({'code': 500, 'message': str(e)}, 500)
    
    def do_OPTIONS(self):
        self.send_json({'code': 200, 'message': 'OK'})

    # ========== 物料模块 ==========
    def get_materials(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        keyword = params.get('keyword', [''])[0]
        category_id = params.get('category_id', [None])[0]
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        where = "WHERE s.is_deleted = 0"
        if keyword:
            where += f" AND (s.name LIKE '%{keyword}%' OR s.sku_code LIKE '%{keyword}%' OR s.brand LIKE '%{keyword}%')"
        if category_id:
            where += f" AND s.category_id = {category_id}"
        
        cursor.execute(f"SELECT COUNT(*) FROM material_sku s {where}")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"""
            SELECT s.id, s.sku_code, s.name, s.brand, s.sale_price, s.cost_price,
                   s.category_id, c.name as category_name, s.main_image, 
                   s.stock_quantity, s.unit, s.status, s.created_at
            FROM material_sku s 
            LEFT JOIN material_category c ON s.category_id = c.id 
            {where}
            ORDER BY s.created_at DESC
            LIMIT {page_size} OFFSET {offset}
        """)
        
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({dict(row)})
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_categories(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code, parent_id FROM material_category WHERE is_deleted = 0")
        items = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return {'code': 200, 'data': items}
    
    def get_stats(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM material_sku WHERE status = 'active' AND is_deleted = 0")
        active = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM material_category WHERE is_deleted = 0")
        categories = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT c.id, c.name, c.code, COUNT(s.id) as count
            FROM material_category c
            LEFT JOIN material_sku s ON c.id = s.category_id AND s.is_deleted = 0
            WHERE c.is_deleted = 0
            GROUP BY c.id
            ORDER BY count DESC
        """)
        category_stats = [{'id': r[0], 'name': r[1], 'code': r[2], 'count': r[3]} for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {
            'total': total, 'active': active, 'inactive': total - active,
            'categories': categories, 'by_category': category_stats
        }}
    
    def get_material_options(self):
        return {'code': 200, 'data': {
            'calc_types': [{'value': 'area', 'label': '按面积', 'unit': 'm²'}],
            'sku_status': [{'value': 'active', 'label': '上架', 'type': 'success'}, {'value': 'inactive', 'label': '下架', 'type': 'info'}]
        }}

    # ========== 客户模块 ==========
    def get_customers(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        keyword = params.get('keyword', [''])[0]
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0, 'page': page, 'page_size': page_size}}
        
        where = "WHERE is_deleted = 0"
        if keyword:
            where += f" AND (name LIKE '%{keyword}%' OR phone LIKE '%{keyword}%')"
        
        cursor.execute(f"SELECT COUNT(*) FROM customers {where}")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM customers {where} ORDER BY created_at DESC LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_customer_stats(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'total': 0, 'this_month': 0, 'by_status': {}}}
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        conn.close()
        return {'code': 200, 'data': {'total': total, 'this_month': 0, 'by_status': {}}}
    
    def get_customer_options(self):
        return {'code': 200, 'data': {
            'status_list': ['待跟进', '跟进中', '已签约', '已完成', '已流失'],
            'customer_types': ['潜在客户', '已接触', '意向客户', '签约客户', '老客户'],
            'sources': ['自然进店', '线上咨询', '老客户推荐', '楼盘合作', '其他'],
            'priorities': ['高', '中', '低']
        }}
    
    def create_customer(self, data):
        return {'code': 200, 'data': {'id': 1, 'message': '创建成功'}}

    # ========== 员工模块 ==========
    def get_employees(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM employees WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM employees WHERE is_deleted = 0 LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_employee_options(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': []}
        
        cursor.execute("SELECT id, name FROM employees WHERE is_deleted = 0 AND status = 'active'")
        items = [{'id': r['id'], 'name': r['name']} for r in cursor.fetchall()]
        conn.close()
        return {'code': 200, 'data': items}
    
    def create_employee(self, data):
        return {'code': 200, 'data': {'id': 1, 'message': '创建成功'}}

    # ========== 合同模块 ==========
    def get_contracts(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contracts'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM contracts WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM contracts WHERE is_deleted = 0 LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total}}
    
    def create_contract(self, data):
        return {'code': 200, 'data': {'id': 1, 'message': '创建成功'}}

    # ========== 楼盘模块 ==========
    def get_buildings(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buildings'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM buildings WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM buildings WHERE is_deleted = 0 LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total}}
    
    def create_building(self, data):
        return {'code': 200, 'data': {'id': 1, 'message': '创建成功'}}

    # ========== 报价模块 ==========
    def get_quotes(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotes'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM quotes WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM quotes WHERE is_deleted = 0 LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total}}
    
    def create_quote(self, data):
        return {'code': 200, 'data': {'id': 1, 'message': '创建成功'}}

    # ========== 方案模块 ==========
    def get_schemes(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer_schemes'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM customer_schemes WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM customer_schemes WHERE is_deleted = 0 LIMIT {page_size} OFFSET {offset}")
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total}}
    
    def create_scheme(self, data):
        return {'code': 200, 'data': {'id': 1, 'scheme_no': 'SC001', 'message': '创建成功'}}

    # ========== 认证模块 ==========
    def auth_login(self, data):
        return {'code': 200, 'data': {'token': 'mock_token_12345', 'user': {'id': 1, 'username': 'admin', 'name': '管理员'}}}


if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 完整API服务器")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    server = HTTPServer(('0.0.0.0', 8080), APIHandler)
    server.serve_forever()
