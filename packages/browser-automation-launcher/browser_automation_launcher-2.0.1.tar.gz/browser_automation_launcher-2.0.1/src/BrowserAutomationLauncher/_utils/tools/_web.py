"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-05-19
Author: Martian Bugs
Description: web 相关的工具库
"""

from urllib.parse import quote, unquote, urlencode, urlparse


class WebTools:
    @staticmethod
    def url_same(a: str, b: str):
        """
        检查两个 url 是否域名及路径是否一致

        Args:
            a: 第一个 url
            b: 第二个 url
        Returns:
            是否一致
        """

        a_result = urlparse(a)
        b_result = urlparse(b)

        is_same = a_result.netloc == b_result.netloc and a_result.path == b_result.path

        return is_same

    @staticmethod
    def url_append_params(url: str, params: dict):
        """
        给 url 添加参数

        Args:
            url: 原始 url
            params: 参数字典
        Returns:
            带参数的 url
        """

        _url = url.rstrip('?')
        params_str = urlencode(params)
        return f'{_url}?{params_str}'

    @staticmethod
    def url_decode(url: str):
        """
        url 链接解码

        Args:
            url: 待解码的 url
        Returns:
            解码后的 url
        """

        return unquote(url)

    @staticmethod
    def url_encode(url: str):
        """
        url 链接编码

        Ags:
            url: 待编码的 url
        Returns:
            编码后的 url
        """

        return quote(url)
