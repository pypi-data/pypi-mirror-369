"""
收藏
"""
from enum import Enum
from typing import Optional
from pydantic import Field, BaseModel

class CollectionType(str, Enum):
    AshareCompany = "AshareCompany" # 个股

# 收藏
class Collection(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    collectable_type: str = Field(..., min_length=1, max_length=50, description="收藏对象", examples=[CollectionType.AshareCompany.value])
    collectable_id: Optional[list] | None = Field(..., description="收藏对象id", examples=[[1,2]])