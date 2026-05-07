"""
文件上传工具
支持: 图片、Office文档、音视频分类存储
"""
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

# 文件类型配置
FILE_CONFIG = {
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'],
        'max_size': 30 * 1024 * 1024,  # 30MB (增大以支持高分辨率图片)
        'folder': 'images',
        'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg+xml']
    },
    'office': {
        'extensions': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.csv'],
        'max_size': 50 * 1024 * 1024,  # 50MB
        'folder': 'documents',
        'mime_types': [
            'application/msword', 'application/vnd.openxmlformats-officedocument',
            'application/vnd.ms-excel', 'application/vnd.ms-powerpoint',
            'application/pdf', 'text/plain', 'text/csv'
        ]
    },
    'audio': {
        'extensions': ['.mp3', '.wav', '.wma', '.aac', '.flac', '.m4a', '.ogg'],
        'max_size': 100 * 1024 * 1024,  # 100MB
        'folder': 'audio',
        'mime_types': ['audio/mpeg', 'audio/wav', 'audio/x-ms-wma', 'audio/aac', 'audio/flac', 'audio/mp4', 'audio/ogg']
    },
    'video': {
        'extensions': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v'],
        'max_size': 500 * 1024 * 1024,  # 500MB
        'folder': 'video',
        'mime_types': ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-ms-wmv', 
                       'video/x-flv', 'video/x-matroska', 'video/webm']
    }
}

# 上传根目录
UPLOAD_ROOT = Path(__file__).parent.parent.parent / 'upload'


def ensure_upload_dirs():
    """确保上传目录存在"""
    for config in FILE_CONFIG.values():
        folder_path = UPLOAD_ROOT / config['folder']
        folder_path.mkdir(parents=True, exist_ok=True)
        # 按年月创建子目录
        now = datetime.now()
        (folder_path / f"{now.year}" / f"{now.month:02d}").mkdir(parents=True, exist_ok=True)


def get_file_category(filename):
    """根据文件名判断文件类型分类"""
    ext = Path(filename).suffix.lower()
    for category, config in FILE_CONFIG.items():
        if ext in config['extensions']:
            return category
    return None


def validate_file(file_obj, category=None):
    """
    验证文件
    
    Args:
        file_obj: FileStorage 对象
        category: 指定分类，None则自动检测
    
    Returns:
        (is_valid, error_message, detected_category)
    """
    if not file_obj or not file_obj.filename:
        return False, '未选择文件', None
    
    filename = secure_filename(file_obj.filename)
    detected_category = get_file_category(filename)
    
    if not detected_category:
        return False, f'不支持的文件类型: {Path(filename).suffix}', None
    
    # 如果指定了分类，检查是否匹配
    if category and category != detected_category:
        return False, f'文件类型与指定分类不符', detected_category
    
    config = FILE_CONFIG[detected_category]
    
    # 检查文件大小
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)
    
    if file_size > config['max_size']:
        max_mb = config['max_size'] / (1024 * 1024)
        return False, f'文件大小超过限制 ({max_mb}MB)', detected_category
    
    if file_size == 0:
        return False, '文件不能为空', detected_category
    
    return True, None, detected_category


def save_upload_file(file_obj, category=None, custom_name=None):
    """
    保存上传文件
    
    Args:
        file_obj: FileStorage 对象
        category: 文件分类 (image/office/audio/video)，None则自动检测
        custom_name: 自定义文件名（不含扩展名）
    
    Returns:
        {
            'success': bool,
            'file_id': str,
            'original_name': str,
            'saved_name': str,
            'category': str,
            'file_path': str,
            'file_url': str,
            'file_size': int,
            'mime_type': str,
            'error': str
        }
    """
    # 验证文件
    is_valid, error_msg, detected_category = validate_file(file_obj, category)
    if not is_valid:
        return {
            'success': False,
            'error': error_msg
        }
    
    category = category or detected_category
    config = FILE_CONFIG[category]
    
    # 生成保存路径
    now = datetime.now()
    relative_dir = Path(config['folder']) / str(now.year) / f"{now.month:02d}"
    absolute_dir = UPLOAD_ROOT / relative_dir
    absolute_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    original_name = secure_filename(file_obj.filename)
    ext = Path(original_name).suffix.lower()
    
    if custom_name:
        saved_name = f"{custom_name}{ext}"
    else:
        # 使用 UUID + 时间戳
        unique_id = uuid.uuid4().hex[:8]
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        name_part = Path(original_name).stem[:20]  # 限制原文件名长度
        saved_name = f"{timestamp}_{name_part}_{unique_id}{ext}"
    
    # 保存文件
    file_path = absolute_dir / saved_name
    try:
        file_obj.save(str(file_path))
    except Exception as e:
        return {
            'success': False,
            'error': f'保存文件失败: {str(e)}'
        }
    
    # 计算文件哈希
    file_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    
    # 生成文件ID
    file_id = f"{category}_{file_hash.hexdigest()[:16]}"
    
    # 获取文件大小
    file_size = file_path.stat().st_size
    
    return {
        'success': True,
        'file_id': file_id,
        'original_name': original_name,
        'saved_name': saved_name,
        'category': category,
        'file_path': str(file_path.relative_to(UPLOAD_ROOT)),
        'file_url': f"/upload/{relative_dir.as_posix()}/{saved_name}",
        'file_size': file_size,
        'mime_type': file_obj.content_type or 'application/octet-stream'
    }


def delete_upload_file(file_path):
    """删除上传的文件"""
    try:
        full_path = UPLOAD_ROOT / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def get_upload_stats():
    """获取上传文件统计"""
    stats = {}
    for category, config in FILE_CONFIG.items():
        folder = UPLOAD_ROOT / config['folder']
        if not folder.exists():
            stats[category] = {'count': 0, 'size': 0}
            continue
        
        total_size = 0
        file_count = 0
        
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        stats[category] = {
            'count': file_count,
            'size': total_size,
            'size_human': format_size(total_size)
        }
    
    return stats


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


# 阿里云 OSS 配置（预留）
OSS_CONFIG = {
    'access_key_id': os.getenv('OSS_ACCESS_KEY_ID', ''),
    'access_key_secret': os.getenv('OSS_ACCESS_KEY_SECRET', ''),
    'bucket_name': os.getenv('OSS_BUCKET_NAME', ''),
    'endpoint': os.getenv('OSS_ENDPOINT', ''),
    'cdn_domain': os.getenv('OSS_CDN_DOMAIN', '')
}


def upload_to_oss(local_path, oss_key):
    """
    上传文件到阿里云 OSS（预留接口）
    
    Args:
        local_path: 本地文件路径
        oss_key: OSS 上的存储路径
    
    Returns:
        (success, url_or_error)
    """
    try:
        import oss2
        
        auth = oss2.Auth(OSS_CONFIG['access_key_id'], OSS_CONFIG['access_key_secret'])
        bucket = oss2.Bucket(auth, OSS_CONFIG['endpoint'], OSS_CONFIG['bucket_name'])
        
        bucket.put_object_from_file(oss_key, str(local_path))
        
        # 生成访问 URL
        if OSS_CONFIG['cdn_domain']:
            url = f"https://{OSS_CONFIG['cdn_domain']}/{oss_key}"
        else:
            url = f"https://{OSS_CONFIG['bucket_name']}.{OSS_CONFIG['endpoint']}/{oss_key}"
        
        return True, url
        
    except ImportError:
        return False, '请先安装 oss2: pip install oss2'
    except Exception as e:
        return False, str(e)


def sync_upload_folder_to_oss(category=None):
    """
    同步上传文件夹到阿里云 OSS（预留接口）
    
    Args:
        category: 指定分类同步，None则同步全部
    
    Returns:
        {
            'success': int,
            'failed': int,
            'errors': list
        }
    """
    result = {'success': 0, 'failed': 0, 'errors': []}
    
    categories = [category] if category else FILE_CONFIG.keys()
    
    for cat in categories:
        folder = UPLOAD_ROOT / FILE_CONFIG[cat]['folder']
        if not folder.exists():
            continue
        
        for file_path in folder.rglob('*'):
            if not file_path.is_file():
                continue
            
            # 构建 OSS key
            relative_path = file_path.relative_to(UPLOAD_ROOT)
            oss_key = f"upload/{relative_path.as_posix()}"
            
            success, msg = upload_to_oss(file_path, oss_key)
            if success:
                result['success'] += 1
            else:
                result['failed'] += 1
                result['errors'].append(f"{file_path}: {msg}")
    
    return result
