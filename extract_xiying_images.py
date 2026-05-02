"""
提取西映Excel文件中的图片
"""
import zipfile
import os
import shutil
from pathlib import Path

# Excel文件路径
EXCEL_FILES = [
    r'D:\desktop\报价标准数据库\供应链\西映\西映24-餐厅系统-餐椅.xlsx',
    r'D:\desktop\报价标准数据库\供应链\西映\西映24-餐厅系统-餐桌.xlsx',
    r'D:\desktop\报价标准数据库\供应链\西映\西映24-家居配套系统-妆台&书桌&边几.xlsx'
]

# 输出目录
OUTPUT_DIR = r'D:\desktop\DESIGNARY-SYS-V3.0\xiying_images'

def extract_images_from_excel(excel_path, output_subdir):
    """从Excel文件中提取图片"""
    print(f"\n处理文件: {os.path.basename(excel_path)}")
    
    # 创建临时目录解压
    temp_dir = os.path.join(OUTPUT_DIR, 'temp_' + os.path.basename(excel_path).replace('.xlsx', ''))
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # 解压Excel文件 (Excel是ZIP格式)
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 图片通常在 xl/media/ 目录下
        media_dir = os.path.join(temp_dir, 'xl', 'media')
        
        if not os.path.exists(media_dir):
            print(f"  未找到图片目录: {media_dir}")
            return 0
        
        # 创建输出子目录
        out_dir = os.path.join(OUTPUT_DIR, output_subdir)
        os.makedirs(out_dir, exist_ok=True)
        
        # 复制图片
        image_count = 0
        for filename in os.listdir(media_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                src_path = os.path.join(media_dir, filename)
                # 重命名为更有意义的名称
                new_name = f"{output_subdir}_{filename}"
                dst_path = os.path.join(out_dir, new_name)
                shutil.copy2(src_path, dst_path)
                image_count += 1
                print(f"  提取: {new_name}")
        
        print(f"  共提取 {image_count} 张图片")
        return image_count
        
    except Exception as e:
        print(f"  错误: {e}")
        return 0
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    print("=" * 60)
    print("西映Excel图片提取工具")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_images = 0
    
    # 处理餐椅
    total_images += extract_images_from_excel(EXCEL_FILES[0], 'chair')
    
    # 处理餐桌
    total_images += extract_images_from_excel(EXCEL_FILES[1], 'table')
    
    # 处理家居配套
    total_images += extract_images_from_excel(EXCEL_FILES[2], 'furniture')
    
    print("\n" + "=" * 60)
    print(f"提取完成! 总计: {total_images} 张图片")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
