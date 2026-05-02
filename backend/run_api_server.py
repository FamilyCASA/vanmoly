"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - API服务器
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
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        try:
            if path == '/api/v3/' or path == '/api/v3':
                response = {'code': 200, 'data': {'version': '3.0.8'}, 'message': 'OK'}
            elif path == '/api/v3/health':
                response = {'code': 200, 'data': {'status': 'ok'}, 'message': 'OK'}
            elif path == '/api/v3/materials':
                response = self.get_materials(params)
            elif path == '/api/v3/materials/categories':
                response = self.get_categories()
            elif path == '/api/v3/materials/stats':
                response = self.get_stats()
            else:
                response = {'code': 404, 'message': 'Not found'}
        except Exception as e:
            response = {'code': 500, 'message': str(e)}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
    
    def get_materials(self, params):
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('page_size', ['10'])[0])
        keyword = params.get('keyword', [''])[0]
        category_id = params.get('category_id', [None])[0]
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        where = "WHERE s.is_deleted = 0 AND s.status = 'active'"
        if keyword:
            where += f" AND (name LIKE '%{keyword}%' OR sku_code LIKE '%{keyword}%' OR brand LIKE '%{keyword}%')"
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
            items.append({
                'id': row['id'],
                'sku_code': row['sku_code'],
                'name': row['name'],
                'brand': row['brand'] or '',
                'sale_price': row['sale_price'],
                'cost_price': row['cost_price'],
                'category_id': row['category_id'],
                'category_name': row['category_name'] or '',
                'main_image': row['main_image'] or '',
                'stock_quantity': row['stock_quantity'],
                'unit': row['unit'] or '',
                'status': row['status'],
                'created_at': row['created_at']
            })
        
        conn.close()
        return {'code': 200, 'data': {'items': items, 'total': total, 'page': page, 'page_size': page_size}}
    
    def get_categories(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, code, parent_id FROM material_category WHERE is_deleted = 0")
        rows = cursor.fetchall()
        
        items = [{'id': r['id'], 'name': r['name'], 'code': r['code'], 'parent_id': r['parent_id']} for r in rows]
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
        
        # 按分类统计
        cursor.execute("""
            SELECT c.id, c.name, c.code, COUNT(s.id) as count
            FROM material_category c
            LEFT JOIN material_sku s ON c.id = s.category_id AND s.is_deleted = 0 AND s.status = 'active'
            WHERE c.is_deleted = 0
            GROUP BY c.id
            ORDER BY count DESC
        """)
        category_stats = []
        for row in cursor.fetchall():
            category_stats.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'count': row[3]
            })
        
        conn.close()
        return {'code': 200, 'data': {
            'total': total, 
            'active': active, 
            'inactive': total - active, 
            'categories': categories,
            'by_category': category_stats
        }}
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - API服务器")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    server = HTTPServer(('0.0.0.0', 8080), APIHandler)
    server.serve_forever()
