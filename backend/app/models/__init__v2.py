"""数据模型包 V2.0 - 多数据库架构"""

# HR系统模型 (hr.db)
from app.models.hr_v2 import (
    Department,
    Position,
    Employee,
    EmployeeSalary,
    PerformanceReview,
    EmployeePoints,
    PointsTransaction,
    CareerPath,
    TrainingRecord,
    EmployeeWelfare
)

# 线索系统模型 (lead.db)
from app.models.lead_v3 import (
    Lead,
    LeadFollow,
    PublicSeaLead,
    LeadDistributionLog,
    LeadChannelStats
)

# CRM系统模型 (crm.db)
from app.models.crm_v2 import (
    Customer,
    CustomerFollow,
    CustomerServiceHistory
)

__all__ = [
    # HR系统
    'Department',
    'Position',
    'Employee',
    'EmployeeSalary',
    'PerformanceReview',
    'EmployeePoints',
    'PointsTransaction',
    'CareerPath',
    'TrainingRecord',
    'EmployeeWelfare',
    # 线索系统
    'Lead',
    'LeadFollow',
    'PublicSeaLead',
    'LeadDistributionLog',
    'LeadChannelStats',
    # CRM系统
    'Customer',
    'CustomerFollow',
    'CustomerServiceHistory',
]
