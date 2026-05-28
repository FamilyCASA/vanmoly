"""数据模型包 - 统一版本（V3.0 最终）"""

from app.models.case import (
    CaseStudy, CaseMedia, CaseTimeline, CaseFile,
    CaseSubscription, CaseLead, CaseTemplate,
    CaseNotification, CaseOperationLog, CaseWorkflowTimeline,
    CasePhase, CaseSpaceRendering, CaseRenderingItem,
    CaseSpaceMaterial, CaseSlideConfig, SlideTemplate,
)
from app.models.lead_v2 import (
    Lead, LeadFollow, LeadPoint, LeadDistribution, LeadChannelStat
)
from app.models.appointment import Appointment
from app.models.coupon import Coupon, CouponClaim
from app.models.material import SalesMaterial
from app.models.article import Article
# HR 基础模型（Department/Position/Employee + 基础合同/绩效）
from app.models.hr import (
    Department, Position, Employee,
    EmployeeContract, EmployeePerformance,
)
# HR 扩展模型（薪资/积分/晋升/培训等）
from app.models.hr_v2 import (
    EmployeeSalary, PerformanceReview, EmployeePoints, PointsTransaction,
    CareerPath, TrainingRecord, EmployeeWelfare,
    PointsRule, PointsAudit, TeamBuilding, PointsExchange,
)
from app.models.frontend_config import (
    PageConfig, ComponentConfig, ResourceConfig,
    NavigationConfig, ThemeConfig, FrontendVersion
)
from app.models.customer import Customer, CustomerFollow
from app.models.material_sku import (
    MaterialSKU, MaterialCategory, MaterialVariant, MaterialSupplier
)
from app.models.service_workflow import (
    WorkflowNode, CustomerWorkflow, WorkflowNodeRecord
)
from app.models.contract import (
    Contract, ContractTemplate, ContractPayment, ContractChange
)
from app.models.building import (
    Building, BuildingFollow, BuildingCustomer
)
from app.models.quote import (
    Quote, QuoteItem, QuoteTemplate
)
from app.models.scheme import (
    CustomerScheme, SchemeItem
)
from app.models.auth_v2 import (
    UserV2, PasswordResetToken, LoginLog, Store, DigitalAssetTransfer
)
# 空间配置 V3.2（新增）
from app.models.space_config import (
    CaseSpaceConfig, CaseSpaceConfigItem, QuoteSpaceInstance, MaterialExclusiveRule
)
from app.models.craft_process import CraftProcess

__all__ = [
    # 案例管理
    'CaseStudy', 'CaseMedia', 'CaseTimeline', 'CaseFile',
    'CaseSubscription', 'CaseLead', 'CaseTemplate',
    'CaseNotification', 'CaseOperationLog', 'CaseWorkflowTimeline',
    'CasePhase', 'CaseSpaceRendering', 'CaseRenderingItem',
    'CaseSpaceMaterial', 'CaseSlideConfig', 'SlideTemplate',
    # 线索 V2.0
    'Lead', 'LeadFollow', 'LeadPoint', 'LeadDistribution', 'LeadChannelStat',
    # 预约
    'Appointment',
    # 优惠券
    'Coupon', 'CouponClaim',
    # 物料
    'SalesMaterial', 'MaterialSKU', 'MaterialCategory', 'MaterialVariant', 'MaterialSupplier',
    # 文章
    'Article',
    # HR（统一来自 hr.py）
    'Department', 'Position', 'Employee',
    'EmployeeContract', 'EmployeePerformance',
    'EmployeeSalary', 'PerformanceReview', 'EmployeePoints', 'PointsTransaction',
    'CareerPath', 'TrainingRecord', 'EmployeeWelfare',
    'PointsRule', 'PointsAudit', 'TeamBuilding', 'PointsExchange',
    # 合同
    'Contract', 'ContractTemplate', 'ContractPayment', 'ContractChange',
    # 楼盘
    'Building', 'BuildingFollow', 'BuildingCustomer',
    # 报价
    'Quote', 'QuoteItem', 'QuoteTemplate',
    # 前端配置（来自其他模块）
    'PageConfig', 'ComponentConfig', 'ResourceConfig',
    'NavigationConfig', 'ThemeConfig', 'FrontendVersion',
    # 客户
    'Customer', 'CustomerFollow',
    # 服务流程
    'WorkflowNode', 'CustomerWorkflow', 'WorkflowNodeRecord',
    # 方案
    'CustomerScheme', 'SchemeItem',
    # 认证 V2.0
    'UserV2', 'PasswordResetToken', 'LoginLog', 'Store', 'DigitalAssetTransfer',
    # 空间配置 V3.2（新增）
    'CaseSpaceConfig', 'CaseSpaceConfigItem', 'QuoteSpaceInstance', 'MaterialExclusiveRule',
    # 特殊工艺
    'CraftProcess',
]
