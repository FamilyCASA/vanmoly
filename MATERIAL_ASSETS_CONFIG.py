# 物料资源目录配置
# 将此配置添加到后端 config.py

MATERIAL_ASSETS = {
    'base_path': r'D:\resources\vanmoly\materials',
    'images': {
        'chairs': r'D:\resources\vanmoly\materials\images\chairs',
        'tables': r'D:\resources\vanmoly\materials\images\tables',
        'furniture': r'D:\resources\vanmoly\materials\images\furniture',
        'thumbnails': r'D:\resources\vanmoly\materials\images\thumbnails',
    },
    'videos': r'D:\resources\vanmoly\materials\videos',
    'url_prefix': '/materials',
}

# 静态文件服务配置（生产环境Nginx示例）
# location /materials/images/ {
#     alias D:/resources/vanmoly/materials/images/;
#     expires 30d;
# }
# location /materials/videos/ {
#     alias D:/resources/vanmoly/materials/videos/;
#     expires 30d;
# }
