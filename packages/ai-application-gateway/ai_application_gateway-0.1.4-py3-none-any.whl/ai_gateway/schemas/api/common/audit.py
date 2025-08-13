"""
更新日志
"""

from typing import Optional

from pydantic import Field, BaseModel

# 收藏
from enum import Enum

class ChangeType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class AuditableType(str, Enum):
    USER = "User"
    USER_SUBSCRIPTION = "UserSubscription"
    USER_COLLECTION = "UserCollection"

class Audit(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    auditable_id: int = Field(..., description="模型对应id", examples=[1])
    auditable_type: AuditableType = Field(..., description="模型名称(User/UserSubscription/UserCollection)", examples=[AuditableType.USER])
    changes: Optional[dict] = Field(default=None, description="字段变更前后内容{field: [previous, after]}", examples=[{
      "user_id": "T021530",
      "auditable_id": 1,
      "auditable_type": "User",
      "changes": {
        "emails": ["test1@example.com","test2@example.com"]
      },
      "change_type": "update",
      "created_at": "2023-01-01T12:00:00Z"
    }])
    change_type: ChangeType = Field(..., description="数据变更类型(create/update/delete)", examples=[ChangeType.UPDATE])