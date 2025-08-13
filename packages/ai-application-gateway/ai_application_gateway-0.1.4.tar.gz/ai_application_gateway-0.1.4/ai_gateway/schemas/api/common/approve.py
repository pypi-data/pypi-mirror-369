"""
通用审批
"""

from typing import List, Optional
from enum import Enum
from datetime import datetime

from pydantic import Field, BaseModel, conint

# 审批对象类型
class ApproveTypeCode(str, Enum):
    Opportunity_Subscribable_Email = "Opportunity_Subscribable_Email" # 商机挖掘：订阅审批通知
    AshareCompany_Subscribable = "AshareCompany_Subscribable" # 个股商机订阅

# 添加审批
class AddDelApprove(BaseModel):
    business_type: str = Field(..., description="业务类型：Opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    object_user_id: str = Field(..., min_length=1, max_length=20, description="审批对象用户ID", example="T021530")
    object_ids: list[int] = Field(..., min_items=1, description="审批对象ids（数组）", example=[1,2,3,4,5])
    approve_type_code: ApproveTypeCode = Field(..., min_length=1, max_length=50, description="审批类型编码", example="Opportunity_Subscribable_Email")
    approve_user_id: str | None = Field(default=None, min_length=1, max_length=20, description="审批用户id", example="T021530")
    approve_description: str | None = Field(default=None, description="审批描述", example="商机订阅审批，收件人邮箱：a@126.com，抄送人邮箱：b@126.com")


# 审批状态
class ApproveState(Enum):
    WAIT = 0
    AGREE = 1
    REJECT = 2

# 审批排序字段（值为物理表字段，用于映射）
class ApproveOrderField(Enum):
    created_at = "created_at"  # 创建时间
    approve_at = "approve_at"  # 审批时间
    updated_at = "updated_at"  # 更新时间
    approve_state = "approve_state"  # 审批状态
    object_user_id = "object_user_id"  # 被审批人工号
    object_user_name = "object_user_name"  # 被审批人姓名
    approve_user_id = "approve_user_id"  # 审批人工号
    approve_user_name = "approve_user_name"  # 审批人姓名


# 获取审批数据列表
class InGetApproves(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    approve_type_code: ApproveTypeCode = Field(..., min_length=1, max_length=50, description="审批类型编码", example="Opportunity_Subscribable_Email")
    approve_state: List[ApproveState] | None = Field(default=None, min_items=1, description="审批状态: 0-未审批，1-已通过，2-已驳回", examples=[[0]])
    approve_user_id: str | None = Field(default=None, max_length=20, description="审批用户id", examples=[""])
    order: Optional[dict] = Field(default=None, description="多字段排序，1-倒序、2-正序", examples=[{
        "created_at": 1,
        "approve_at": 1,
    }])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 审批状态处理
class ApproveStateProcess(Enum):
    AGREE = 1
    REJECT = 2

# 审批
class InApprove(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    approve_type_code: ApproveTypeCode = Field(..., min_length=1, max_length=50, description="审批类型编码", example="Opportunity_Subscribable_Email")
    id: list[int] = Field(..., min_items=1, description="审批主键ID", example=[1,2])
    approve_state: ApproveStateProcess = Field(..., description="审批状态: 1-已通过，2-已驳回", examples=[1])
    approve_user_id: str = Field(..., min_length=1, max_length=20, description="审批人工号", examples=["T021530"])
    approve_user_name: str = Field(..., min_length=1, max_length=20, description="审批人姓名", examples=["李云"])
    approve_user_email: str = Field(..., min_length=1, max_length=100, description="审批人邮箱", examples=["1@126.com"])
    cc_users: List[dict] = Field(default=None, description="抄送人", examples=[[
    {
        "user_id": "T000001",
        "user_name": "张三",
        "email": "1@126.com"
    },
    {
        "user_id": "T000002",
        "user_name": "李四",
        "email": "1@126.com"
    }
    ]])
    object_user_name: Optional[str] = Field(default=None, min_length=1, max_length=20, description="被审批人姓名", examples=["刘江"])

# 获取单条审批
class InGetApprove(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    approve_type_code: ApproveTypeCode = Field(..., min_length=1, max_length=50, description="审批类型编码", example="Opportunity_Subscribable_Email")
    id: int = Field(..., description="审批主键ID", example="1")
    approve_state: List[ApproveState] | None = Field(default=None, min_items=1, description="审批状态: 0-未审批，1-已通过，2-已驳回", examples=[[0]])
