"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 稳定版API服务器
使用socketserver.ThreadingTCPServer避免SIGKILL
"""
import os
import sys
import json
import sqlite3
import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vanmoly_v3.db')

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

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
            if path in ['/api/v3/', '/api/v3']:
                self.send_json({'code': 200, 'data': {'version': '3.0.9', 'modules': ['materials', 'customers', 'employees', 'contracts', 'buildings', 'quotes', 'schemes']}, 'message': 'OK'})
            elif path == '/api/v3/health':
                self.send_json({'code': 200, 'data': {'status': 'ok', 'db_exists': os.path.exists(DB_PATH)}, 'message': 'OK'})
            elif path == '/api/v3/materials':
                self.send_json(self.get_materials(params))
            elif path == '/api/v3/materials/categories':
                self.send_json(self.get_categories())
            elif path == '/api/v3/materials/stats':
                self.send_json(self.get_stats())
            elif path == '/api/v3/customers':
                self.send_json(self.get_customers(params))
            elif path == '/api/v3/customers/stats':
                self.send_json(self.get_customer_stats())
            elif path == '/api/v3/employees':
                self.send_json(self.get_employees(params))
            elif path == '/api/v3/contracts':
                self.send_json(self.get_contracts(params))
            elif path == '/api/v3/buildings':
                self.send_json(self.get_buildings(params))
            elif path == '/api/v3/quotes':
                self.send_json(self.get_quotes(params))
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
                self.send_json({'code': 200, 'data': {'token': 'mock_token', 'user': {'id': 1, 'username': 'admin'}}, 'message': 'OK'})
            else:
                self.send_json({'code': 200, 'data': {'message': 'Created'}, 'message': 'OK'})
        except Exception as e:
            self.send_json({'code': 500, 'message': str(e)}, 500)
    
    def do_OPTIONS(self):
        self.send_json({'code': 200, 'message': 'OK'})

    def get_materials(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = min(int(params.get('page_size', ['20'])[0]), 100)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute("""
            SELECT s.id, s.sku_code, s.name, s.brand, s.sale_price, s.cost_price,
                   s.category_id, c.name as category_name, s.main_image, 
                   s.stock_quantity, s.unit, s.status, s.created_at
            FROM material_sku s 
            LEFT JOIN material_category c ON s.category_id = c.id 
            WHERE s.is_deleted = 0
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        
        items = [dict(r) for r in cursor.fetchall()]
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
        
        cursor.execute("SELECT COUNT(*) FROM material_category WHERE is_deleted = 0")
        categories = cursor.fetchone()[0]
        
        conn.close()
        return {'code': 200, 'data': {'total': total, 'categories': categories}}
    
    def get_customers(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'items': [], 'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        cursor.execute("SELECT * FROM customers WHERE is_deleted = 0 ORDER BY created_at DESC LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_customer_stats(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        if not cursor.fetchone():
            conn.close()
            return {'code': 200, 'data': {'total': 0}}
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0")
        total = cursor.fetchone()[0]
        
        conn.close()
        return {'code': 200, 'data': {'total': total}}
    
    def get_employees(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
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
        cursor.execute("SELECT * FROM employees WHERE is_deleted = 0 LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_contracts(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
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
        cursor.execute("SELECT * FROM contracts WHERE is_deleted = 0 LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_buildings(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
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
        cursor.execute("SELECT * FROM buildings WHERE is_deleted = 0 LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_quotes(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
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
        cursor.execute("SELECT * FROM quotes WHERE is_deleted = 0 LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_schemes(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['20'])[0])
        
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
        cursor.execute("SELECT * FROM customer_schemes WHERE is_deleted = 0 LIMIT ? OFFSET ?", (page_size, offset))
        items = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}


if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 稳定版API服务器")
    print("=" * 50)
    print(f"数据库: {DB_PATH}")
    print(f"数据库存在: {os.path.exists(DB_PATH)}")
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    server = ThreadedHTTPServer(('0.0.0.0', 8080), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
