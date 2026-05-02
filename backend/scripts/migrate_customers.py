"""
客户数据迁移脚本
从 vanmoly-distilled 导入客户数据到 V3.0
"""
import sqlite3
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.customer import Customer, CustomerFollow
from datetime import datetime

# 旧系统数据库路径
OLD_CUSTOMER_DB = r'D:\desktop\vanmoly-distilled\instance\customer.db'


def migrate_customers():
    """迁移客户数据"""
    app = create_app()

    with app.app_context():
        # 连接旧数据库
        old_conn = sqlite3.connect(OLD_CUSTOMER_DB)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()

        # 获取旧客户数据
        old_cursor.execute("""
            SELECT * FROM customers WHERE is_deleted = 0
        """)
        old_customers = old_cursor.fetchall()

        print(f"找到 {len(old_customers)} 个客户需要迁移")

        migrated_count = 0
        skipped_count = 0

        for row in old_customers:
            old_customer = dict(row)

            # 检查是否已存在（根据手机号）
            existing = Customer.query.filter_by(phone=old_customer.get('phone')).first()
            if existing:
                print(f"跳过已存在客户: {old_customer.get('name')} ({old_customer.get('phone')})")
                skipped_count += 1
                continue

            # 创建新客户
            customer = Customer(
                name=old_customer.get('name', ''),
                phone=old_customer.get('phone', ''),
                gender=old_customer.get('gender', '未知'),
                email=old_customer.get('email'),
                wechat=old_customer.get('wechat'),
                address=old_customer.get('address'),
                province=old_customer.get('province'),
                city=old_customer.get('city'),
                district=old_customer.get('district'),
                street=old_customer.get('street'),
                detail_address=old_customer.get('detail_address'),
                building_name=old_customer.get('building_name'),
                source=old_customer.get('source'),
                budget=old_customer.get('budget'),
                house_type=old_customer.get('house_type'),
                house_area=old_customer.get('house_area'),
                requirements=old_customer.get('requirements'),
                style_preference=old_customer.get('style_preference'),
                customer_type=old_customer.get('customer_type', '已接触'),
                status=old_customer.get('status', '待跟进'),
                priority=old_customer.get('priority', '普通'),
                owner_id=old_customer.get('owner_id'),
                follow_count=old_customer.get('follow_count', 0),
                remark=old_customer.get('remark'),
                tenant_id=old_customer.get('tenant_id', '0'),
                is_deleted=False
            )

            # 处理时间字段
            if old_customer.get('last_follow'):
                try:
                    customer.last_follow = datetime.fromisoformat(old_customer['last_follow'])
                except:
                    pass

            if old_customer.get('next_follow'):
                try:
                    customer.next_follow = datetime.fromisoformat(old_customer['next_follow'])
                except:
                    pass

            if old_customer.get('created_at'):
                try:
                    customer.created_at = datetime.fromisoformat(old_customer['created_at'])
                except:
                    pass

            db.session.add(customer)
            migrated_count += 1

            if migrated_count % 10 == 0:
                print(f"已迁移 {migrated_count} 个客户...")

        # 提交事务
        db.session.commit()
        old_conn.close()

        print(f"\n迁移完成!")
        print(f"成功迁移: {migrated_count} 个客户")
        print(f"跳过重复: {skipped_count} 个客户")


if __name__ == '__main__':
    migrate_customers()
