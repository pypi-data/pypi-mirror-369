"""
邮件
"""

from typing import Optional, List
from pydantic import Field, BaseModel

class Email(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    to_list: List[str] = Field(default_factory=list, description="收件人邮箱列表", min_items=1, examples=[["example@example.com", "example2@example.com"]])
    subject: str = Field(..., description="邮件主题", examples=["主题"])  # 邮件主题
    text: str = Field(..., description="邮件正文(HTML格式)", examples=["正文"])  # 邮件正文(HTML格式)
    attachments: List[str] | None  = Field(default=None, description="附件路径(可选), 可以是本地路径或HTTP URL", examples=[["/Users/dianguan/Desktop/citic/ai-application-gateway/data/send_email/daily_result.csv"]])
