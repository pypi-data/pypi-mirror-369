from decimal import Decimal


# 格式化Decimal字段
def format_decimal_fields(item):
    for key, value in item.items():
        if isinstance(value, Decimal):
            item[key] = "{0:.10f}".format(value).rstrip('0').rstrip('.')
        # 添加Oracle NUMBER类型处理，先将float转换为字符串，再转换为Decimal，可以避免浮点数精度问题。
        elif isinstance(value, float):
            item[key] = "{0:.10f}".format(Decimal(str(value))).rstrip('0').rstrip('.')
    return item