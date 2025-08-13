"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-07-22
Author: Martian Bugs
Description: 基础工具库
"""

import re
from copy import deepcopy
from typing import Any


class CommonTools:
    @staticmethod
    def str_replace_by_variables(variable_table: dict[str, Any], string: str):
        """
        字符串变量替换. `${}` 包裹的表示变量

        Args:
            variable_table: 变量表
            string: 含变量的字符串
        Returns:
            替换后的字符串
        """

        formated = deepcopy(string)
        for key, value in variable_table.items():
            formated = formated.replace(
                "${" + key + "}", str(value) if not isinstance(value, str) else value
            )

        return formated

    @staticmethod
    def str_cleanup(text: str):
        """
        清理字符串两端的特殊字符和不可见字符，包括空白字符、BOM头（如果存在）以及其他常见的控制字符。
        """

        if not isinstance(text, str):
            return text

        # 1. 去除常见的空白字符（包括空格、制表符、换行符等）
        cleaned_text = text.strip()

        # 2. 去除BOM头 (Byte Order Mark) - 对于UTF-8文件可能存在
        cleaned_text = cleaned_text.lstrip("\ufeff")

        # 3. 去除其他不可见字符和控制字符（例如零宽度非连接符 \u200c）
        # 这里使用正则表达式匹配并替换掉非打印字符，但保留常见的可打印字符和标点符号
        # \p{C} 匹配 Unicode 控制字符、格式字符、未分配代码点、私有使用字符
        # \u0000-\u001F, \u007F-\u009F 是 ASCII/Latin-1 控制字符
        # \u200B-\u200F, \u202A-\u202E, \u2060-\u206F 是常见的零宽度字符或格式控制字符
        # 这个正则可以根据实际需要调整，以匹配更广泛或更窄的特殊字符
        cleaned_text = re.sub(
            r"[\u0000-\u001F\u007F-\u009F\u200B-\u200F\u202A-\u202E\u2060-\u206F]",
            "",
            cleaned_text,
        )

        return cleaned_text
