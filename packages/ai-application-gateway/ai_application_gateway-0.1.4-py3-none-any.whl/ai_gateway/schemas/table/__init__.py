import os
import importlib.util

# 添加已导入模块的跟踪集合
_imported_modules = set()

def import_module(name):
    # 检查模块是否已经导入
    if name in _imported_modules:
        return None
    try:
        module = importlib.import_module(name)
        _imported_modules.add(name)
        return module
    except ImportError:
        return None


def scan_modules(directory, base_package):
    """递归扫描目录下的所有 Python 模块"""
    result = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        # 跳过 __pycache__ 和以 __ 开头的文件/目录
        if item.startswith("__"):
            continue
            
        if os.path.isdir(item_path):
            # 处理子目录
            sub_package = f"{base_package}.{item}"
            result.extend(scan_modules(item_path, sub_package))
        elif item.endswith(".py"):
            # 处理 Python 文件
            module_name = item[:-3]
            full_module_name = f"{base_package}.{module_name}"
            module = import_module(full_module_name)
            if module:
                result.append(full_module_name)
                short_name = full_module_name.split(".")[-1]
                if short_name not in globals():  # 添加检查，避免重复导入
                    globals()[short_name] = module
    
    return result


current_dir = os.path.dirname(__file__)
package_name = "ai_gateway.schemas.table"

# 扫描所有模块
modules = scan_modules(current_dir, package_name)

# 设置 __all__ 为所有模块的短名称
__all__ = [m.split(".")[-1] for m in modules]

