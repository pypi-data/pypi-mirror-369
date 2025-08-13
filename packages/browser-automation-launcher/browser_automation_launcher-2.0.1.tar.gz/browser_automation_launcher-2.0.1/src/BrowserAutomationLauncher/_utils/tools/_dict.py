"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-05-19
Author: Martian Bugs
Description: 字典相关工具库
"""

from copy import deepcopy


class DictUtils:
    @staticmethod
    def dict_mapping(data: dict, dict_table: dict[str, str]):
        """
        字典表字段映射

        Args:
            data: 待映射的字典
            dict_table: 字典表
        """

        result = {}
        for text, key in dict_table.items():
            result[text] = data.get(key)

        return result

    @staticmethod
    def dict_format__float(
        data: dict,
        fields: list[str] = None,
        precision: int = 2,
        exclude_fields: list[str] = None,
    ):
        """
        将字典数据中的指定字段格式化为 float 类型

        Args:
            data: 待格式化的字典
            fields: 需要格式化的字段列表, 如果为 None, 则表示所有字段
            precision: 保留小数位数, 默认 2 位
            exclude_fields: 排除的字段列表
        Returns:
            格式化后的字典
        """

        _fields = fields if fields and isinstance(fields, list) else data.keys()
        _exclude_fields = (
            exclude_fields
            if exclude_fields and isinstance(exclude_fields, list)
            else []
        )

        _data = deepcopy(data)
        for field in _fields:
            if field not in _data or field in _exclude_fields:
                continue

            value = _data[field]
            if not isinstance(value, (int, float)):
                continue

            _data[field] = value / 10**precision

        return _data

    @staticmethod
    def dict_format__round(
        data: dict,
        fields: list[str] = None,
        precision: int = 2,
        exclude_fields: list[str] = None,
    ):
        """
        将字典数据中的指定字段作四舍五入处理

        Args:
            data: 待格式化的字典
            fields: 需要格式化的字段列表, 如果为 None, 则表示所有字段
            precision: 保留小数位数, 默认 2 位
            exclude_fields: 排除的字段列表
        Returns:
            格式化后的字典
        """

        _fields = fields if fields and isinstance(fields, list) else data.keys()
        _exclude_fields = (
            exclude_fields
            if exclude_fields and isinstance(exclude_fields, list)
            else []
        )

        _data = deepcopy(data)
        for field in _fields:
            if field not in _data or field in _exclude_fields:
                continue

            value = _data[field]
            if not isinstance(value, float):
                continue

            _data[field] = round(value, precision)

        return _data

    @staticmethod
    def dict_format__ratio(
        data: dict,
        fields: list[str] = None,
        ratio: int = 2,
        exclude_fields: list[str] = None,
    ):
        """
        将字典数据中的指定字段转为比率, 例如百分比/千分比等

        Args:
            data: 待格式化的字典
            fields: 需要格式化的字段列表, 如果为 None, 则表示所有字段
            ratio: 比率, 默认 2 及百分比
            exclude_fields: 排除的字段列表
        Returns:
            格式化后的字典
        """

        _fields = fields if fields and isinstance(fields, list) else data.keys()
        _exclude_fields = (
            exclude_fields
            if exclude_fields and isinstance(exclude_fields, list)
            else []
        )

        _data = deepcopy(data)
        for field in _fields:
            if field not in _data or field in _exclude_fields:
                continue

            value = _data[field]
            if not isinstance(value, (int, float)):
                continue

            _data[field] = value * (10**ratio)

        return _data

    @staticmethod
    def dict_format__strip(
        data: dict,
        fields: list[str] = None,
        prefix: list[str] = None,
        suffix: list[str] = None,
        exclude_fields: list[str] = None,
    ):
        """
        格式化字典数据中的指定字段, 去除前后空格及指定前后缀

        Args:
            data: 待格式化的字典
            fields: 需要格式化的字段列表, 如果为 None, 则表示所有字段
            prefix: 需要去除的前缀列表
            suffix: 需要去除的后缀列表
            exclude_fields: 排除的字段列表
        Returns:
            格式化后的字典
        """

        _fields = fields if fields and isinstance(fields, list) else data.keys()
        _exclude_fields = (
            exclude_fields
            if exclude_fields and isinstance(exclude_fields, list)
            else []
        )

        _data = deepcopy(data)
        for field in _fields:
            if field not in _data or field in _exclude_fields:
                continue

            value = _data[field]
            if not isinstance(value, str):
                continue

            value = value.strip()
            if prefix and isinstance(prefix, list):
                for c in prefix:
                    value = value.lstrip(c)

            if suffix and isinstance(suffix, list):
                for c in suffix:
                    value = value.rstrip(c)

            _data[field] = value

        return _data

    @staticmethod
    def dict_format__number(
        data: dict, fields: list[str] = None, exclude_fields: list[str] = None
    ):
        """
        格式化字典数据中的指定字段, 将字符串转为数字

        Args:
            data: 待格式化的字典
            fields: 需要格式化的字段列表, 如果为 None, 则表示所有字段
            exclude_fields: 排除的字段列表
        Returns:
            格式化后的字典
        """

        _fields = fields if fields and isinstance(fields, list) else data.keys()
        _exclude_fields = (
            exclude_fields
            if exclude_fields and isinstance(exclude_fields, list)
            else []
        )

        _data = deepcopy(data)
        for field in _fields:
            if field not in _data or field in _exclude_fields:
                continue

            value = _data[field]
            if not isinstance(value, str):
                continue

            try:
                value = value.replace(',', '')
                value = float(value) if '.' in value else int(value)
            except ValueError:
                continue

            _data[field] = value

        return _data
