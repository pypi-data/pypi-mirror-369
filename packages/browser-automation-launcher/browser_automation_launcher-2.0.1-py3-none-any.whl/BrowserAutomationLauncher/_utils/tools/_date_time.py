"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-05-19
Author: Martian Bugs
Description: 日期时间工具库
"""

from datetime import datetime, timedelta, timezone


class DateTimeTools:
    @staticmethod
    def date_yesterday(pattern='%Y-%m-%d'):
        """
        获取前一天的日期

        Args:
            pattern: 日期格式
        """

        return DateTimeTools.date_calculate(days=1, pattern=pattern)

    @staticmethod
    def date_calculate(days: int, pattern='%Y-%m-%d', date: str = None):
        """
        日期计算

        Args:
            days: 日期偏移量, 负数表示向后推
            pattern: 日期格式
            date: 基准日期, 留空则表示今天
        """

        base_date = datetime.strptime(date, pattern) if date else datetime.now()
        return (base_date - timedelta(days=days)).strftime(pattern)

    @staticmethod
    def date_diff_days(a: str, b: str, pattern='%Y-%m-%d'):
        """
        计算两个日期间隔的天数
        - 正数表示 a 日期在 b 日期之后

        Args:
            a: 日期字符串
            b: 日期字符串
        """

        a_dt = datetime.strptime(a, pattern)
        b_dt = datetime.strptime(b, pattern)

        return (a_dt - b_dt).days

    @staticmethod
    def date_to_timestamp(date: str, pattern='%Y-%m-%d'):
        """
        将日期转为 10 位时间戳

        Args:
            date: 日期字符串
            pattern: 日期格式
        """

        dt = datetime.strptime(date, pattern)
        dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
        return int(dt.timestamp())

    @staticmethod
    def datetime_to_timestamp(date_time: str, pattern='%Y-%m-%d %H:%M:%S'):
        """
        将时间时间转为 13 位时间戳

        Args:
            date_time: 日期时间字符串
            pattern: 日期时间格式
        """

        dt = datetime.strptime(date_time, pattern)
        dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
        return int(dt.timestamp() * 1000)

    @staticmethod
    def date_range(begin_date: str, end_date: str, pattern='%Y-%m-%d'):
        """
        根据起始日期和结束日期生成日期列表

        Args:
            begin_date: 起始日期字符串
            end_date: 结束日期字符串
            pattern: 日期格式
        Returns:
            日期列表
        """

        begin_dt, end_dt = [
            datetime.strptime(date, pattern) for date in (begin_date, end_date)
        ]
        diff = (end_dt - begin_dt).days
        date_list = [
            (begin_dt + timedelta(days=i)).strftime(pattern) for i in range(diff + 1)
        ]

        return date_list

    @staticmethod
    def date_to_utc(date: str, pattern='%Y-%m-%d', replace_with_nowtime=False):
        """
        获取指定日期的UTC的时间字符串

        Args:
            date: 指定日期
            pattern: 日期格式
            replace_with_nowtime: 是否将时间部分替换为当前时间
        """

        shanghai_tz = timezone(timedelta(hours=8))

        dp = datetime.strptime(date, pattern).replace(tzinfo=shanghai_tz)
        if replace_with_nowtime is True:
            now = datetime.now(shanghai_tz)
            dp = dp.replace(
                hour=now.hour,
                minute=now.minute,
                second=now.second,
                microsecond=now.microsecond,
            )

        utc_time = dp.astimezone(timezone.utc).isoformat(timespec='milliseconds')
        return utc_time.replace('+00:00', 'Z')

    @staticmethod
    def timestamp_to_str(timestamp: int | str, pattern='%Y-%m-%d %H:%M:%S'):
        """
        将时间戳转为日期时间字符串

        Args:
            timestamp: 时间戳
            pattern: 日期时间格式
        Returns:
            日期时间字符串
        """

        return datetime.fromtimestamp(int(timestamp)).strftime(pattern)

    @staticmethod
    def seconds_to_time(seconds: int):
        """
        秒数转为时间字符串

        Args:
            seconds: 秒数
        Returns:
            时间字符串, 格式为 'xx:xx'
        """

        m, s = divmod(seconds, 60)
        _, m = divmod(m, 60)
        return f'{m:02d}:{s:02d}'
