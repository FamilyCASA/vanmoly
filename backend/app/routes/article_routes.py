"""
文章/动态模块路由
API端点: /api/v3/articles
"""
from flask import Blueprint, request, jsonify
from datetime import datetime


article_bp = Blueprint('article', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@article_bp.route('/articles', methods=['GET'])
def get_articles():
    """获取文章列表"""
    return api_response(data={'items': [], 'total': 0})


@article_bp.route('/articles', methods=['POST'])
def create_article():
    """创建文章"""
    return api_response(code=404, message='功能开发中')
