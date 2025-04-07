#!/usr/bin/env python3  # 指定 Python 解释器路径，使脚本可执行

import argparse  # 导入 argparse 模块，用于解析命令行参数
import logging  # 导入 logging 模块，用于记录日志
import sys  # 导入 sys 模块，用于系统相关操作
import traceback  # 导入 traceback 模块，用于异常跟踪

from logging import FileHandler  # 从 logging 模块导入 FileHandler，用于日志文件记录
from mscclang2chakra_converter import MSCCL2ChakraConverter  # 导入 MSCCL2ChakraConverter 处理 msccl 格式输入

def get_logger(log_filename: str) -> logging.Logger:
    """
    配置日志记录器：
    - 记录到文件（DEBUG 级别）
    - 记录到标准输出（WARNING 及以上）
    """
    formatter = logging.Formatter(
        "%(levelname)s [%(asctime)s] %(message)s",  # 日志格式，包含日志级别、时间戳和消息
        datefmt="%m/%d/%Y %I:%M:%S %p"  # 日期时间格式（MM/DD/YYYY HH:MM:SS AM/PM）
    )

    file_handler = FileHandler(log_filename, mode="w")  # 创建日志文件处理器，以写入模式打开文件
    file_handler.setLevel(logging.DEBUG)  # 设置文件日志级别为 DEBUG
    file_handler.setFormatter(formatter)  # 应用日志格式

    stream_handler = logging.StreamHandler()  # 创建标准输出日志处理器
    stream_handler.setLevel(logging.WARNING)  # 设置标准输出日志级别为 WARNING
    stream_handler.setFormatter(formatter)  # 应用日志格式

    logger = logging.getLogger(__file__)  # 获取当前文件的日志记录器
    logger.setLevel(logging.DEBUG)  # 设置日志记录器级别为 DEBUG
    logger.addHandler(file_handler)  # 添加文件日志处理器
    logger.addHandler(stream_handler)  # 添加标准输出日志处理器

    return logger  # 返回配置好的日志记录器

def main() -> None:
    """
    主函数：
    - 解析命令行参数
    - 根据输入类型调用相应的转换器
    - 记录日志并处理异常
    """
    parser = argparse.ArgumentParser(
        description="Execution Trace Converter"  # 命令行工具的描述信息
    )

    # 添加命令行参数
    parser.add_argument(
        "--input_type",
        type=str,
        default=None,
        required=True,
        help="Input execution trace type"  # 指定输入类型，例如 "msccl"
    )
    parser.add_argument(
        "--input_filename",
        type=str,
        default=None,
        required=True,
        help="Input execution trace filename"  # 指定输入文件名
    )
    parser.add_argument(
        "--output_filename",
        type=str,
        default=None,
        required=True,
        help="Output Chakra execution trace filename"  # 指定输出文件名
    )
    parser.add_argument(
        "--log_filename",
        type=str,
        default="debug.log",
        help="Log filename"  # 指定日志文件名称，默认为 "debug.log"
    )
    parser.add_argument(
        "--coll_size",
        type=int,
        default=1048576,
        help="Collective size in Bytes"  # 指定集合通信大小，默认值为 1MB (1048576 字节)
    )

    args = parser.parse_args()  # 解析命令行参数

    logger = get_logger(args.log_filename)  # 获取日志记录器
    logger.debug(" ".join(sys.argv))  # 记录命令行输入的所有参数

    try:
        # 检查输入类型是否为 "msccl"
        if args.input_type == "msccl":
            converter = MSCCL2ChakraConverter(
                args.input_filename,  # 输入文件名
                args.output_filename,  # 输出文件名
                args.coll_size,  # 集合通信大小
                logger  # 传递日志记录器
            )
            converter.convert()  # 执行转换
        else:
            logger.error(f"{args.input_type} unsupported")  # 记录不支持的输入类型
            sys.exit(1)  # 退出程序，返回错误状态码 1

    except Exception as e:
        traceback.print_exc()  # 打印异常信息
        logger.debug(traceback.format_exc())  # 记录异常信息到日志
        sys.exit(1)  # 退出程序，返回错误状态码 1

# 当脚本直接执行时，调用 main() 函数
if __name__ == "__main__":
    main()
