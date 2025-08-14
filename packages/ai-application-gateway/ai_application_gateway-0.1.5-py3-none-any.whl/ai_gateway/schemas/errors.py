from enum import IntEnum

# HTTP状态码
class HttpStatusCode(IntEnum):
    SUCCESS_200 = 200                   # 处理成功
    BAD_REQUEST_400 = 400               # 参数错误
    UNAUTHORIZED_401 = 401              # 鉴权失败或Token超时
    FORBIDDEN_403 = 403                 # 服务器理解请求但拒绝执行
    NOT_FOUND_404 = 404                 # 客户端请求的资源在服务器上不存在
    UNPROCESSABLE_ENTITY_422 = 422      # 不可处理的实体
    TOO_MANY_REQUESTS_429 = 429         # 请求并发超额
    NO_API_PERMISSION_434 = 434         # 暂无API权限
    INTERNAL_SERVER_ERROR_500 = 500     # 服务器处理请求时发生错误
    SERVICE_UNAVAILABLE_503 = 503       # 服务不可用，如：数据库服务器暂时不可用或过载或正在维护
    SYSTEM_BUSY_529 = 529               # 系统繁忙，请求超时


# 业务错误码
class ErrorCode(IntEnum):
    SUCCESS_200 = 200                   # 处理成功

    # 应用错误码
    PLAT_APP_1000 = 1000                # 应用不存在
    PLAT_APP_1001 = 1001                # 应用维护中
    PLAT_APP_1002 = 1002                # 应用已停止

    # 接口错误码
    PLAT_INTERFACE_1100 = 1100          # 接口不存在
    PLAT_INTERFACE_1101 = 1101          # 接口维护中
    PLAT_INTERFACE_1102 = 1102          # 接口已停止

    # API Key 错误码
    PLAT_API_KEY_1200 = 1200            # API Key 已存在
    PLAT_API_KEY_1201 = 1201            # API Key 不存在
    PLAT_API_KEY_1202 = 1202            # API Key 已过期
    PLAT_API_KEY_1203 = 1203            # API Key 已禁用
    PLAT_API_KEY_1204 = 1204            # API Key IP白名单限制
    PLAT_API_KEY_1205 = 1205            # API Key 操作失败

    # 接口日志错误码
    PLAT_INTERFACE_LOG_1300 = 1300     # 接口日志写入失败

    # 接口授权错误码
    PLAT_INTERFACE_AUTH_1400 = 1400     # 接口授权不存在

    # db错误码
    PLAT_DBS_DB_2000 = 2000             # db 错误
    # redis错误码
    PLAT_DBS_REDIS_2100 = 2100          # redis 错误
    # es错误码
    PLAT_DBS_ES_2200 = 2200             # es 错误
    # minio错误码
    PLAT_DBS_MINIO_2300 = 2300          # minio 错误


    # ETF智能营销
    ETF_INTELLIGENT_MARKETING_5100 = 5100 # ETF智能营销 业务逻辑失败

    # DEMO
    DEMO_SIMPLE_10000 = 10000             # DEMO SIMPLE 业务逻辑失败
    DEMO_DB_CURD_11000 = 11000            # DEMO DB_CURD 业务逻辑失败
