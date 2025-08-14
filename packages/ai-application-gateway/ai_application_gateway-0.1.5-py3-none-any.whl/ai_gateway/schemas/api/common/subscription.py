"""
订阅
"""
from enum import Enum
from typing import Optional
from pydantic import Field, BaseModel


class SubscriptionType(str, Enum):
    AshareCompany = "AshareCompany" # 个股

# 收藏
class Subscription(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    subscribable_type: str = Field(..., min_length=1, max_length=50, description="订阅对象", examples=[SubscriptionType.AshareCompany.value])
    subscribable_id: Optional[list] | None = Field(..., description="订阅对象id", examples=[[1,2]])