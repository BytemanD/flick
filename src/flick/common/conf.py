from typing import Optional

import confz
from pydantic import BaseModel


class ServerConfigs(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5000


class AppConfigs(confz.BaseConfig):
    debug: bool = False
    logfile: Optional[str] = None

    server: ServerConfigs = ServerConfigs()

    # CONFIG_SOURCES = [
    #     confz.FileSource(
    #         file=os.getenv("MYAPP_CONFIG", str(pathlib.Path("etc", "flick.yaml"))),
    #         optional=True,  # 配置文件可选
    #     ),
    #     confz.EnvSource(
    #         prefix="FLICK_",
    #         allow_all=True,  # 允许所有环境变量
    #         nested_separator="_",  # 将 MYAPP_DB__URL 映射为 db.url
    #     ),
    #     confz.CLArgSource(
    #         # prefix="conf-",
    #         nested_separator="-",  # 将 --db-url 映射为 db_url
    #         remap={
    #             "logfile": "logfile",  # 映射命令行参数到配置字段
    #         },
    #     ),
    # ]


CONF: AppConfigs = AppConfigs()
