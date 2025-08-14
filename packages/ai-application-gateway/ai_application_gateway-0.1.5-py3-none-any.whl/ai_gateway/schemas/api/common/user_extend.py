"""
用户扩展
"""

from typing import Optional
from pydantic import Field, BaseModel

class UserExtend(BaseModel):
    business_type: str = Field(..., description="业务类型：opportunity-商机挖掘", examples=["opportunity"])
    user_id: str = Field(..., min_length=1, max_length=20, description="用户ID", examples=["T021530"])
    sub_emails: Optional[list] | None = Field(default=None, description="订阅邮箱(支持多个)", examples=[["test1@example.com","test2@example.com"]])
