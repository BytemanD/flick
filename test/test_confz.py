import argparse
import os

import confz
from flick.common import conf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str)
    parser.add_argument("--port", type=int)
    parser.add_argument("--debug", action="store_true")  # 关键：--debug 直接生效
    args = parser.parse_args()
    cli_args = {k: v for k, v in vars(args).items() if v is not None}

    # conf.CONF.update_from_cli(cli_args)  # 更新配置实例
    # conf.AppConfigs.CONFIG_SOURCES.append(confz.DataSource(data=cli_args))

    # conf.CONF.debug = conf.AppConfigs()  # 创建配置实例，启用调试模式
    setattr(conf.CONF, "debug", args.debug)  # 设置 debug 属性
    # CONF.
    print(conf.CONF.model_dump_json(indent=4))  # 输出配置的 JSON 格式
    print(conf.CONF.debug)  # 输出配置的 debug 状态
    print(conf.CONF.logfile)  # 输出配置的 logfile 路径，如果未设置则
    # confz.CLArgSource({"debug": True})


if __name__ == "__main__":
    main()
