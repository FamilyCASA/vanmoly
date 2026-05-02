"""
员工管理模块 - 常量定义（V3.0 最终版）

模型已迁移至 app.models.hr
本文件仅保留枚举常量，供其他模块引用
"""

# 员工状态选项
EMPLOYEE_STATUS = [
    ('active', '在职'),
    ('probation', '试用期'),
    ('resigned', '已离职'),
    ('leave', '休假中'),
]

# 员工角色选项
EMPLOYEE_ROLES = [
    ('admin', '超级管理员'),
    ('manager', '店长/经理'),
    ('supervisor', '主管'),
    ('employee', '普通员工'),
]

# 合同类型
CONTRACT_TYPES = [
    ('labor', '劳动合同'),
    ('probation', '试用期合同'),
    ('renewal', '续签合同'),
    ('part_time', '兼职合同'),
]
