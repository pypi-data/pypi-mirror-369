"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-07-23
Author: Martian Bugs
Description: 多功能下载器
"""

import re
from os import makedirs, path
from sys import stdout
from time import time
from typing import Literal
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests
from requests import Response


class Downloader:
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }

    def _get_filename_from_response(self, response: Response):
        """
        从 Requests 响应中获取文件名, 优先从 Content-Disposition 头获取，其次从 URL 解析.

        Args:
            response: 响应体对象
        Returns:
            获取到的文件名
        """

        cd = response.headers.get('content-disposition')
        if not cd:
            parsed_url = urlparse(response.url)
            filename = path.basename(parsed_url.path)
            return unquote(filename) if filename else None

        filename_result = re.search(r'filename="(.*?)"', cd)
        if filename_result:
            return unquote(filename_result.group(1))

        filename_result = re.search(r'filename\*=(.*?)\'\'(.*)', cd)
        if filename_result:
            return unquote(filename_result.group(2), encoding=filename_result.group(1))

        return None

    def _filename_conflict(self, on_conflict: str, filename: str):
        """
        文件名冲突处理

        Args:
            on_conflict: 冲突处理方式
            filename: 原始文件名
        Returns:
            处理冲突后的文件名
        """

        if on_conflict == 'overwrite':
            return filename

        if on_conflict == 'skip':
            return

        if on_conflict == 'rename':
            name_without_ext, ext = path.splitext(filename)
            timestamp = int(time() * 1000)
            filename = f'{name_without_ext}_{timestamp}{ext}'
            return filename

        raise ValueError(f'无效的文件冲突处理方式: {on_conflict}')

    def download(
        self,
        url: str,
        save_path: str,
        method: Literal['GET', 'POST'] = 'GET',
        rename: str = None,
        file_exists: Literal['skip', 'overwrite', 'rename'] = 'overwrite',
        headers: dict = None,
        cookies: dict | str = None,
        data: dict = None,
        json_data: dict = None,
        timeout: int | float = 60,
        proxies: dict = None,
        show_progress=True,
    ):
        """
        下载文件
        """

        _save_path = path.realpath(save_path)
        if not path.exists(_save_path):
            makedirs(_save_path, exist_ok=True)

        if (
            not method
            or not isinstance(method, str)
            or method.upper() not in ['GET', 'POST']
        ):
            raise RuntimeError(f'不支持的 HTTP 方法: {method}')

        session = requests.Session()

        session.headers.update(self._headers)
        if headers and isinstance(headers, dict):
            session.headers.update(headers)

        if cookies and isinstance(cookies, (dict, str)):
            cookies_str = (
                ';'.join([f'{k}={v}' for k, v in cookies.items()])
                if isinstance(cookies, dict)
                else cookies
            )
            session.headers.update({'Cookie': cookies_str})

        if proxies and isinstance(proxies, dict):
            session.proxies.update(proxies)

        request_params = {
            'stream': True,
            'allow_redirects': True,
            'timeout': timeout if isinstance(timeout, (float, int)) else 60,
        }

        print(f'下载文件: {url}')
        if data and isinstance(data, dict):
            request_params['data'] = data
        if json_data and isinstance(json_data, dict):
            request_params['json'] = json_data

        response = session.request(method=method.upper(), url=url, **request_params)
        response.raise_for_status()  # 检查 HTTP 错误，如 4xx 或 5xx 错误

        filename = (
            rename
            if rename
            else (self._get_filename_from_response(response) or str(uuid4()))
        )
        file_path = path.join(_save_path, filename)

        if path.exists(file_path):
            filename = self._filename_conflict(file_exists, filename)
            if not filename:
                return

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        start_time = time()

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                if show_progress is not True:
                    continue

                # 显示下载进度
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    elapsed_time = time() - start_time
                    speed = (
                        (downloaded_size / 1024) / elapsed_time
                        if elapsed_time > 0
                        else 0
                    ) / 1024
                    progress_info = f'\r下载进度: {progress:.2f}% ({downloaded_size / (1024 * 1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB) | 速度: {speed:.2f} MB/s'
                    stdout.write('\r' + progress_info)
                    stdout.flush()

        print(f'\n下载完成: {file_path}')

        return file_path
