/**
 * D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - Node.js API服务器
 * 轻量级，避免Python SIGKILL问题
 */
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'instance', 'vanmoly_v3.db');
const PORT = 8000;

// 模拟数据存储
const mockData = {
  materials: [],
  categories: [],
  customers: [],
  employees: [],
  contracts: [],
  buildings: [],
  quotes: [],
  schemes: []
};

// 初始化模拟数据
function initMockData() {
  // 12个分类
  const categories = [
    { id: 1, name: '固装家具', code: 'fixed', parent_id: null },
    { id: 2, name: '活动家具', code: 'active', parent_id: null },
    { id: 3, name: '定制家具', code: 'custom', parent_id: null },
    { id: 4, name: '灯具', code: 'lighting', parent_id: null },
    { id: 5, name: '窗帘', code: 'curtain', parent_id: null },
    { id: 6, name: '地毯', code: 'carpet', parent_id: null },
    { id: 7, name: '饰品', code: 'decor', parent_id: null },
    { id: 8, name: '挂画', code: 'painting', parent_id: null },
    { id: 9, name: '花艺', code: 'flower', parent_id: null },
    { id: 10, name: '床品', code: 'bedding', parent_id: null },
    { id: 11, name: '餐厨用品', code: 'kitchen', parent_id: null },
    { id: 12, name: '卫浴用品', code: 'bathroom', parent_id: null }
  ];
  mockData.categories = categories;

  // 928条物料数据
  for (let i = 1; i <= 928; i++) {
    const catId = Math.floor(Math.random() * 12) + 1;
    mockData.materials.push({
      id: i,
      sku_code: `SKU${String(i).padStart(6, '0')}`,
      name: `物料${i}`,
      brand: ['帝标', '高晟', '鲁班', 'D&B 帝标|设记家'][Math.floor(Math.random() * 4)],
      sale_price: Math.floor(Math.random() * 5000) + 500,
      cost_price: Math.floor(Math.random() * 3000) + 300,
      category_id: catId,
      category_name: categories.find(c => c.id === catId)?.name,
      main_image: null,
      stock_quantity: Math.floor(Math.random() * 100),
      unit: ['件', '套', '米', '平方米'][Math.floor(Math.random() * 4)],
      status: Math.random() > 0.2 ? 'active' : 'inactive',
      created_at: new Date(Date.now() - Math.random() * 86400000 * 365).toISOString()
    });
  }

  // 5个客户
  for (let i = 1; i <= 5; i++) {
    mockData.customers.push({
      id: i,
      name: `客户${i}`,
      phone: `138${String(Math.floor(Math.random() * 100000000)).padStart(8, '0')}`,
      status: ['待跟进', '跟进中', '已签约'][Math.floor(Math.random() * 3)],
      created_at: new Date().toISOString()
    });
  }

  // 5个员工
  for (let i = 1; i <= 5; i++) {
    mockData.employees.push({
      id: i,
      name: `员工${i}`,
      position: ['全案规划师', '设计师', '项目经理'][Math.floor(Math.random() * 3)],
      department: ['设计部', '工程部', '销售部'][Math.floor(Math.random() * 3)],
      status: 'active',
      created_at: new Date().toISOString()
    });
  }

  // 3个合同
  for (let i = 1; i <= 3; i++) {
    mockData.contracts.push({
      id: i,
      contract_no: `CT${String(i).padStart(4, '0')}`,
      customer_id: i,
      amount: Math.floor(Math.random() * 100000) + 50000,
      status: ['draft', 'signed', 'executing'][Math.floor(Math.random() * 3)],
      created_at: new Date().toISOString()
    });
  }

  // 5个楼盘
  for (let i = 1; i <= 5; i++) {
    mockData.buildings.push({
      id: i,
      name: `楼盘${i}`,
      address: `地址${i}`,
      property_type: ['住宅', '别墅', '公寓'][Math.floor(Math.random() * 3)],
      created_at: new Date().toISOString()
    });
  }

  // 3个报价
  for (let i = 1; i <= 3; i++) {
    mockData.quotes.push({
      id: i,
      quote_no: `QT${String(i).padStart(4, '0')}`,
      customer_id: i,
      total_amount: Math.floor(Math.random() * 100000) + 50000,
      status: ['draft', 'sent', 'approved'][Math.floor(Math.random() * 3)],
      created_at: new Date().toISOString()
    });
  }

  // 3个方案
  for (let i = 1; i <= 3; i++) {
    mockData.schemes.push({
      id: i,
      scheme_no: `SC${String(i).padStart(4, '0')}`,
      name: `方案${i}`,
      customer_id: i,
      style: ['现代', '中式', '北欧'][Math.floor(Math.random() * 3)],
      total_budget: Math.floor(Math.random() * 100000) + 50000,
      created_at: new Date().toISOString()
    });
  }
}

function sendJSON(res, data, statusCode = 200) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': '*'
  });
  res.end(JSON.stringify(data));
}

function paginate(items, page, pageSize) {
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  return {
    items: items.slice(start, end),
    total: items.length,
    page: page,
    page_size: pageSize
  };
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const params = parsedUrl.query;

  // 处理OPTIONS请求
  if (req.method === 'OPTIONS') {
    sendJSON(res, { code: 200, message: 'OK' });
    return;
  }

  // 路由处理
  try {
    // 根路由
    if (path === '/api/v3/' || path === '/api/v3') {
      sendJSON(res, { 
        code: 200, 
        data: { 
          version: '3.0.9', 
          modules: ['materials', 'customers', 'employees', 'contracts', 'buildings', 'quotes', 'schemes'],
          db_exists: fs.existsSync(DB_PATH)
        }, 
        message: 'OK' 
      });
      return;
    }

    // 健康检查
    if (path === '/api/v3/health') {
      sendJSON(res, { code: 200, data: { status: 'ok' }, message: 'OK' });
      return;
    }

    // 登录
    if (path === '/api/v3/auth/login' && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        sendJSON(res, { 
          code: 200, 
          data: { 
            token: 'mock_token_12345', 
            user: { id: 1, username: 'admin', name: '管理员' } 
          }, 
          message: 'OK' 
        });
      });
      return;
    }

    // 物料模块
    if (path === '/api/v3/materials') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.materials, page, pageSize), message: 'OK' });
      return;
    }

    if (path === '/api/v3/materials/categories') {
      sendJSON(res, { code: 200, data: mockData.categories, message: 'OK' });
      return;
    }

    if (path === '/api/v3/materials/stats') {
      const categoryStats = mockData.categories.map(c => ({
        ...c,
        count: mockData.materials.filter(m => m.category_id === c.id).length
      }));
      sendJSON(res, { 
        code: 200, 
        data: { 
          total: mockData.materials.length, 
          categories: mockData.categories.length,
          by_category: categoryStats
        }, 
        message: 'OK' 
      });
      return;
    }

    // 客户模块
    if (path === '/api/v3/customers') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.customers, page, pageSize), message: 'OK' });
      return;
    }

    if (path === '/api/v3/customers/stats') {
      sendJSON(res, { code: 200, data: { total: mockData.customers.length }, message: 'OK' });
      return;
    }

    // 员工模块
    if (path === '/api/v3/employees') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.employees, page, pageSize), message: 'OK' });
      return;
    }

    // 合同模块
    if (path === '/api/v3/contracts') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.contracts, page, pageSize), message: 'OK' });
      return;
    }

    // 楼盘模块
    if (path === '/api/v3/buildings') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.buildings, page, pageSize), message: 'OK' });
      return;
    }

    // 报价模块
    if (path === '/api/v3/quotes') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.quotes, page, pageSize), message: 'OK' });
      return;
    }

    // 方案模块
    if (path === '/api/v3/schemes') {
      const page = parseInt(params.page) || 1;
      const pageSize = Math.min(parseInt(params.page_size) || 20, 100);
      sendJSON(res, { code: 200, data: paginate(mockData.schemes, page, pageSize), message: 'OK' });
      return;
    }

    // 404
    sendJSON(res, { code: 404, message: 'Not found' }, 404);

  } catch (err) {
    sendJSON(res, { code: 500, message: err.message }, 500);
  }
});

// 初始化数据
initMockData();

// 启动服务器
server.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log('D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - Node.js API服务器');
  console.log('='.repeat(50));
  console.log(`数据库路径: ${DB_PATH}`);
  console.log(`数据库存在: ${fs.existsSync(DB_PATH)}`);
  console.log(`物料数据: ${mockData.materials.length} 条`);
  console.log(`分类数据: ${mockData.categories.length} 个`);
  console.log(`客户数据: ${mockData.customers.length} 个`);
  console.log(`员工数据: ${mockData.employees.length} 个`);
  console.log(`合同数据: ${mockData.contracts.length} 个`);
  console.log(`楼盘数据: ${mockData.buildings.length} 个`);
  console.log(`报价数据: ${mockData.quotes.length} 个`);
  console.log(`方案数据: ${mockData.schemes.length} 个`);
  console.log('='.repeat(50));
  console.log(`服务地址: http://0.0.0.0:${PORT}`);
  console.log(`API前缀: /api/v3/`);
  console.log('='.repeat(50));
});
