from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from croniter import croniter

from ai_gateway.config import config
from ai_gateway.curd.plat.app import crud_app
from ai_gateway.dbs.db import get_db,get_url
from ai_gateway.service.business.opportunity_email import send_email_opportunity


# 作业调用方法示例
def copy_task():
    logger.info("同步复制任务")

# 作业调用方法示例
def add_task():
    logger.info("动态添加任务")

# 作业调用据库任务示例
async def sync_apps_task():
    db_gen = None  # 提前初始化用于 finally 块
    try:
        # 添加调试日志
        logger.info("开始同步应用表")
        db_gen = get_db()
        
        # 使用更规范的异步迭代语法
        async for db in db_gen:
            # 这里添加具体的同步逻辑
            apps = await crud_app.get_apps(db)
            logger.info(f"成功同步应用表，共{len(apps)}条记录")

            return  # 提前返回避免执行多余代码
            
        # 添加生成器为空时的错误处理
        raise StopAsyncIteration("数据库连接生成器未返回有效会话")
        
    except StopAsyncIteration as e:
        logger.error(f"数据库连接异常: {str(e)}")
    except Exception as e:
        logger.opt(exception=True).error(f"同步应用表失败: {str(e)}")
    finally:
        # 使用更健壮的资源清理方式
        if db_gen is not None:
            try:
                await db_gen.aclose()
            except Exception as e:
                logger.warning(f"关闭数据库连接异常: {str(e)}")


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._configure_jobstore()

    # 定时任务持久化
    def _configure_jobstore(self):
        jobstore_url = get_url(sync=True)
        self.scheduler.add_jobstore(
            'sqlalchemy',
            alias='default',
            url=jobstore_url,
            tablename='scheduler_jobs'  # 当添加具有相同 ID 的作业时，自动覆盖已存在的作业配置
        )

    def start(self):
        # self.scheduler.add_job(
        #     copy_task,
        #     'interval',
        #     seconds=3,
        #     id='copy_sync',
        #     replace_existing=True
        # )
        #
        # self.scheduler.add_job(
        #     sync_apps_task,
        #     'interval',
        #     seconds=5,
        #     id='app_sync',
        #     replace_existing=True
        # )

        self.scheduler.start()

        # 向所有订阅了商机的用户定时发送邮件
        if config.scheduler.send_email_opportunity_cron:
            self.add_cron_job(send_email_opportunity, config.scheduler.send_email_opportunity_cron, id='send_email_opportunity')
        else:   # 先 self.scheduler.start() 后，才能删除job
            if self.scheduler.get_job('send_email_opportunity', jobstore='default'):
                self.scheduler.remove_job('send_email_opportunity', jobstore='default')

        # logger.info("定时任务调度器已启动")

    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("定时任务调度器已关闭")

    def add_cron_job(self, func, cron_expr, id=None, replace_existing=True):
        # 解析 cron 表达式
        cron_parts = cron_expr.split()
        if len(cron_parts) != 6:
            raise ValueError(f"无效的 cron 表达式：{cron_expr}，必须有 6 个字段。")
        second, minute, hour, day, month, day_of_week = cron_parts

        # 检查 cron 表达式是否有效
        if not croniter.is_valid(cron_expr):
            raise ValueError(f"无效的 cron 表达式：{cron_expr}。")

        # 添加任务到调度器
        self.scheduler.add_job(
            func,
            'cron',
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            id=id,
            replace_existing=replace_existing
        )


scheduler = Scheduler()

# scheduler.scheduler.add_job(
#     add_task,
#     'interval',
#     seconds=3,
#     id='add_sync',
#     replace_existing=True
# )
#
# scheduler.scheduler.remove_job('copy_sync')