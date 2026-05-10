"""
文件上传路由
API端点: /api/v3/upload
"""
from flask import Blueprint, request, jsonify, send_from_directory
from datetime import datetime
import os
from pathlib import Path

from app.utils.upload import (
    save_upload_file, delete_upload_file, get_upload_stats,
    UPLOAD_ROOT, FILE_CONFIG, get_file_category
)

upload_bp = Blueprint('upload', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    单文件上传接口
    
    请求:
    - file: 文件数据 (multipart/form-data)
    - category: 可选，指定分类 (image/office/audio/video)
    
    响应:
    {
        "code": 200,
        "data": {
            "file_id": "xxx",
            "original_name": "原文件名.jpg",
            "saved_name": "20250426_121530_xxx.jpg",
            "category": "image",
            "file_path": "images/2025/04/xxx.jpg",
            "file_url": "/upload/images/2025/04/xxx.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg"
        }
    }
    """
    try:
        if 'file' not in request.files:
            return api_response(code=400, message='未找到文件字段')
        
        file = request.files['file']
        category = request.form.get('category')  # 可选，自动检测
        custom_name = request.form.get('name')   # 可选，自定义文件名
        
        result = save_upload_file(file, category, custom_name)
        
        if not result['success']:
            return api_response(code=400, message=result['error'])
        
        return api_response(data=result)
        
    except Exception as e:
        return api_response(code=500, message=f'上传失败: {str(e)}')


@upload_bp.route('/upload/image', methods=['POST'])
def upload_image():
    """
    图片上传专用接口（兼容前端 /api/v3/upload/image 调用）
    """
    try:
        if 'file' not in request.files:
            return api_response(code=400, message='未找到文件字段')
        
        file = request.files['file']
        custom_name = request.form.get('name')
        print(f'[DEBUG upload_image] filename={repr(file.filename)}, content_type={repr(file.content_type)}, mimetype={repr(file.mimetype)}')
        
        result = save_upload_file(file, category='image', custom_name=custom_name)
        
        if not result['success']:
            return api_response(code=400, message=result['error'])
        
        return api_response(data=result)
        
    except Exception as e:
        return api_response(code=500, message=f'图片上传失败: {str(e)}')


@upload_bp.route('/upload/batch', methods=['POST'])
def upload_batch():
    """
    批量文件上传接口
    
    请求:
    - files[]: 多个文件数据
    - category: 可选，指定分类
    
    响应:
    {
        "code": 200,
        "data": {
            "success": [...],
            "failed": [...]
        }
    }
    """
    try:
        if 'files' not in request.files:
            return api_response(code=400, message='未找到文件字段')
        
        files = request.files.getlist('files')
        category = request.form.get('category')
        
        success_list = []
        failed_list = []
        
        for file in files:
            result = save_upload_file(file, category)
            if result['success']:
                success_list.append(result)
            else:
                failed_list.append({
                    'filename': file.filename,
                    'error': result['error']
                })
        
        return api_response(data={
            'success': success_list,
            'failed': failed_list,
            'total': len(files),
            'success_count': len(success_list),
            'failed_count': len(failed_list)
        })
        
    except Exception as e:
        return api_response(code=500, message=f'批量上传失败: {str(e)}')


@upload_bp.route('/upload/<path:filename>', methods=['GET'])
def serve_file(filename):
    """提供上传文件的访问"""
    try:
        return send_from_directory(UPLOAD_ROOT, filename)
    except FileNotFoundError:
        return api_response(code=404, message='文件不存在')
    except Exception as e:
        return api_response(code=500, message=f'访问文件失败: {str(e)}')


@upload_bp.route('/upload/stats', methods=['GET'])
def upload_stats():
    """获取上传文件统计"""
    try:
        stats = get_upload_stats()
        return api_response(data=stats)
    except Exception as e:
        return api_response(code=500, message=f'获取统计失败: {str(e)}')


@upload_bp.route('/upload/files', methods=['GET'])
def list_files():
    """
    获取文件列表
    
    查询参数:
    - category: 分类筛选
    - page: 页码
    - page_size: 每页数量
    """
    try:
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        files = []
        
        if category:
            # 指定分类
            if category not in FILE_CONFIG:
                return api_response(code=400, message='无效的分类')
            folders = [UPLOAD_ROOT / FILE_CONFIG[category]['folder']]
        else:
            # 所有分类
            folders = [UPLOAD_ROOT / config['folder'] for config in FILE_CONFIG.values()]
        
        for folder in folders:
            if not folder.exists():
                continue
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(UPLOAD_ROOT)
                    file_cat = get_file_category(file_path.name) or 'unknown'
                    
                    files.append({
                        'name': file_path.name,
                        'category': file_cat,
                        'path': str(relative_path),
                        'url': f"/upload/{relative_path.as_posix()}",
                        'size': file_path.stat().st_size,
                        'created': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                    })
        
        # 按时间倒序
        files.sort(key=lambda x: x['created'], reverse=True)
        
        # 分页
        total = len(files)
        start = (page - 1) * page_size
        end = start + page_size
        
        return api_response(data={
            'items': files[start:end],
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        return api_response(code=500, message=f'获取文件列表失败: {str(e)}')


@upload_bp.route('/upload/delete', methods=['POST'])
def delete_file():
    """
    删除上传的文件
    
    请求体:
    {
        "file_path": "images/2025/04/xxx.jpg"
    }
    """
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return api_response(code=400, message='请提供文件路径')
        
        file_path = data['file_path']
        
        # 安全检查：确保路径在 upload 目录内
        full_path = (UPLOAD_ROOT / file_path).resolve()
        if not str(full_path).startswith(str(UPLOAD_ROOT.resolve())):
            return api_response(code=403, message='非法的文件路径')
        
        if delete_upload_file(file_path):
            return api_response(message='文件删除成功')
        else:
            return api_response(code=404, message='文件不存在或删除失败')
            
    except Exception as e:
        return api_response(code=500, message=f'删除失败: {str(e)}')


@upload_bp.route('/upload/config', methods=['GET'])
def upload_config():
    """获取上传配置信息"""
    config = {}
    for category, cfg in FILE_CONFIG.items():
        config[category] = {
            'extensions': cfg['extensions'],
            'max_size': cfg['max_size'],
            'max_size_human': f"{cfg['max_size'] / (1024*1024):.0f}MB",
            'folder': cfg['folder']
        }
    
    return api_response(data={
        'categories': config,
        'upload_root': str(UPLOAD_ROOT)
    })


# 阿里云 OSS 同步接口（预留）
@upload_bp.route('/upload/sync/oss', methods=['POST'])
def sync_to_oss():
    """
    同步上传文件夹到阿里云 OSS
    
    请求体:
    {
        "category": "image"  // 可选，不指定则同步全部
    }
    """
    try:
        from app.utils.upload import sync_upload_folder_to_oss
        
        data = request.get_json() or {}
        category = data.get('category')
        
        result = sync_upload_folder_to_oss(category)
        
        return api_response(data=result)
        
    except ImportError:
        return api_response(code=500, message='请先安装阿里云 OSS SDK: pip install oss2')
    except Exception as e:
        return api_response(code=500, message=f'同步失败: {str(e)}')
