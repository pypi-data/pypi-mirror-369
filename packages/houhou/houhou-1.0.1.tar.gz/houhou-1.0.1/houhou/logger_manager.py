"""
SimpleLogger - 简洁高效的Python日志模块

特性：
1. 简单易用：两行代码即可配置和使用日志
2. 参数可靠：所有配置参数确保生效
3. 灵活输出：支持控制台和文件日志
4. 智能滚动：自动管理日志文件大小和时间
5. 线程安全：适合多线程/多进程环境

使用方法：
1. 配置日志系统（在程序入口调用一次）
2. 在任意模块中获取日志器并记录日志

示例：
    from simple_logger import setup_logging, get_logger

    # 配置日志系统
    setup_logging(
        log_file="app.log",
        log_level="DEBUG",
        max_bytes=10*1024*1024,  # 10MB
        backup_count=5
    )

    # 获取日志器
    logger = get_logger(__name__)
    logger.info("应用程序启动")

高级用法：
    # 动态添加额外日志文件
    from simple_logger import add_file_handler
    add_file_handler("errors.log", level="ERROR")
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional, Union, List

# 模块版本
__version__ = "1.0.1"

# 全局配置状态
_LOGGING_CONFIGURED = False


def setup_logging(
        log_file: Optional[str] = None,
        log_level: Union[str, int] = "INFO",
        format_str: str = "%(asctime)s - %(name)s - [line:%(lineno)d]  - %(levelname)s - %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S",
        console: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        when: Optional[str] = None,
        interval: int = 1,
        file_mode: str = 'a',
        encoding: str = 'utf-8',
        force: bool = False
) -> None:
    """
    配置全局日志系统

    :param log_file: 日志文件路径（None表示不记录到文件）
    :param log_level: 日志级别（'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' 或 logging常量）
    :param format_str: 日志格式字符串
    :param date_format: 日期时间格式
    :param console: 是否在控制台输出日志
    :param max_bytes: 日志文件最大字节数（按大小滚动时使用）
    :param backup_count: 保留的备份文件数量
    :param when: 按时间滚动的时间单位（'S','M','H','D','midnight'）
    :param interval: 滚动间隔（与when配合使用）
    :param file_mode: 文件打开模式（'a'追加，'w'覆盖）
    :param encoding: 文件编码
    :param force: 是否强制重新配置（覆盖现有配置）
    """
    global _LOGGING_CONFIGURED

    # 如果已配置且不需要强制重新配置，则直接返回
    if _LOGGING_CONFIGURED and not force:
        logging.getLogger("simple_logger").warning("日志系统已配置，忽略重复配置")
        return

    # 清除现有配置
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # 设置日志级别
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())
    root_logger.setLevel(log_level)

    # 创建格式化器
    formatter = logging.Formatter(format_str, date_format)

    # 配置控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    # 配置文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 选择文件处理器类型
        if when:
            # 时间滚动日志
            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding=encoding
            )
        else:
            # 大小滚动日志
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding,
                mode=file_mode
            )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    # 更新配置状态
    _LOGGING_CONFIGURED = True

    # 记录配置信息
    logger = logging.getLogger("simple_logger")
    logger.info("日志系统配置完成")
    logger.info(f"日志级别: {logging.getLevelName(log_level)}")
    if console:
        logger.info("控制台输出: 已启用")
    else:
        logger.info("控制台输出: 已禁用")

    if log_file:
        logger.info(f"日志文件: {log_file}")
        if when:
            logger.info(f"滚动策略: 每 {interval} {when} 滚动一次")
        else:
            logger.info(f"滚动策略: 文件大小超过 {max_bytes} 字节时滚动")
        logger.info(f"备份文件数量: {backup_count}")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器

    :param name: 日志器名称（通常使用 __name__）
    :return: 配置好的日志记录器

    注意：如果日志系统未配置，会自动使用默认配置（控制台输出，INFO级别）
    """
    global _LOGGING_CONFIGURED

    if not _LOGGING_CONFIGURED:
        # 自动配置默认日志系统
        setup_logging()

    return logging.getLogger(name)


def add_file_handler(
        log_file: str,
        logger_name: Optional[str] = None,
        level: Union[str, int] = logging.NOTSET,
        format_str: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        when: Optional[str] = None,
        interval: int = 1,
        file_mode: str = 'a',
        encoding: str = 'utf-8'
) -> None:
    """
    为指定日志器添加额外的文件处理器

    :param log_file: 日志文件路径
    :param logger_name: 目标日志器名称（None表示根日志器）
    :param level: 日志级别（仅记录此级别及以上的日志）
    :param format_str: 自定义日志格式
    :param max_bytes: 文件最大字节数（按大小滚动时）
    :param backup_count: 备份文件数量
    :param when: 滚动时间单位
    :param interval: 滚动间隔
    :param file_mode: 文件打开模式
    :param encoding: 文件编码
    """
    # 获取目标日志器
    logger = logging.getLogger(logger_name)

    # 转换日志级别
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 创建文件处理器
    if when:
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding
        )
    else:
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            mode=file_mode
        )

    # 设置级别
    if level != logging.NOTSET:
        handler.setLevel(level)

    # 设置格式
    if format_str:
        handler.setFormatter(logging.Formatter(format_str))
    elif logger.handlers:
        # 复用现有格式
        handler.setFormatter(logger.handlers[0].formatter)
    else:
        # 默认格式
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # 添加到日志器
    logger.addHandler(handler)

    # 记录添加信息
    logger.info(f"添加文件日志处理器: {log_file}")
    if level != logging.NOTSET:
        logger.info(f"此处理器日志级别: {logging.getLevelName(level)}")


def set_log_level(level: Union[str, int]) -> None:
    """
    设置全局日志级别

    :param level: 日志级别（'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' 或 logging常量）
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 更新所有处理器的级别
    for handler in root_logger.handlers:
        handler.setLevel(level)

    root_logger.info(f"全局日志级别已设置为: {logging.getLevelName(level)}")


def is_configured() -> bool:
    """检查日志系统是否已配置"""
    return _LOGGING_CONFIGURED


def reset_logging() -> None:
    """重置日志系统配置"""
    global _LOGGING_CONFIGURED

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    _LOGGING_CONFIGURED = False
    logging.info("日志系统已重置")