"""
FASTAPI API 路由
"""
from fastapi import APIRouter, Depends

from ai_gateway.api.v1.business.ashare_dividend import ashare_dividend_router, ashare_dividend_router_test
from ai_gateway.api.v1.business.opportunity import opportunity_router, opportunity_router_test
from ai_gateway.api.v1.common import subscription
from ai_gateway.api.v1.common.collection import collection_router
from ai_gateway.api.v1.common.subscription import subscription_router
from ai_gateway.api.v1.common.user_extend import user_extend_router
from ai_gateway.api.v1.demo.dbs_test import dbs_test_router
from ai_gateway.api.v1.demo.exception_example import exception_example_router
from ai_gateway.api.v1.demo.llm import llm_router
from ai_gateway.api.v1.plat.api_key import api_key_router
from ai_gateway.api.v1.plat.app import app_router
from ai_gateway.api.v1.plat.interface import interface_router
from ai_gateway.api.v1.plat.interface_auth import interface_auth_router
from ai_gateway.api.v1.plat.interface_log import interface_log_router
from ai_gateway.core.token import verify_token

from ai_gateway.api.v1.plat.auth import auth_router
from ai_gateway.api.v1.demo.simple import simple_router
from ai_gateway.api.v1.demo.db_curd_user import db_curd_user_router
from ai_gateway.api.v1.business.etf import etf_router
from ai_gateway.api.v1.common.email import email_router
from ai_gateway.api.v1.common.approve import approve_router

v1_router = APIRouter()

v1_router.include_router(auth_router, tags=["网关管理：鉴权"])

# v1_router.include_router(ashare_dividend_router, tags=["业务服务：A股分红"])
v1_router.include_router(ashare_dividend_router, tags=["业务服务：A股分红"], dependencies=[Depends(verify_token)])
v1_router.include_router(ashare_dividend_router_test, tags=["业务服务：A股分红_测试"], dependencies=[Depends(verify_token)])
v1_router.include_router(opportunity_router, tags=["业务服务：商机挖掘"], dependencies=[Depends(verify_token)])
v1_router.include_router(opportunity_router_test, tags=["业务服务：商机挖掘_测试"], dependencies=[Depends(verify_token)])
v1_router.include_router(user_extend_router, tags=["通用服务：用户扩展"], dependencies=[Depends(verify_token)])
v1_router.include_router(collection_router, tags=["通用服务：收藏"], dependencies=[Depends(verify_token)])
v1_router.include_router(subscription_router, tags=["通用服务：订阅"], dependencies=[Depends(verify_token)])
v1_router.include_router(email_router, tags=["通用服务：邮件"], dependencies=[Depends(verify_token)])
v1_router.include_router(approve_router, tags=["通用服务：审批"], dependencies=[Depends(verify_token)])

v1_router.include_router(etf_router, tags=["业务服务：ETF 罗盘"], dependencies=[Depends(verify_token)])

v1_router.include_router(app_router, tags=["网关管理：应用"], dependencies=[Depends(verify_token)])
v1_router.include_router(interface_router, tags=["网关管理：接口"], dependencies=[Depends(verify_token)])
v1_router.include_router(api_key_router, tags=["网关管理：API密钥"], dependencies=[Depends(verify_token)])
v1_router.include_router(interface_auth_router, tags=["网关管理：接口授权"], dependencies=[Depends(verify_token)])
v1_router.include_router(interface_log_router, tags=["网关管理：接口日志"], dependencies=[Depends(verify_token)])

v1_router.include_router(simple_router, tags=["标准示例：简单请求"], dependencies=[Depends(verify_token)])
v1_router.include_router(exception_example_router, tags=["标准示例：异常"], dependencies=[Depends(verify_token)])
v1_router.include_router(db_curd_user_router, tags=["标准示例：数据表增删改查"], dependencies=[Depends(verify_token)])
v1_router.include_router(dbs_test_router, tags=["标准示例：数据存储连接测试"], dependencies=[Depends(verify_token)])

v1_router.include_router(llm_router, tags=["标准示例：大模型"], dependencies=[Depends(verify_token)])

