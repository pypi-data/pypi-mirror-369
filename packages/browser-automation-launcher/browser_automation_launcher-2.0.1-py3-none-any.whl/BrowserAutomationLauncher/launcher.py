"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-16
Author: Martian Bugs
Description: 浏览器自动化启动器
"""

from ._browser import Browser, BrowserInitOptions


class Launcher:
    def init_browser(self, init_options: BrowserInitOptions):
        """
        初始化浏览器

        Args:
            init_options: BrowserInitOptions 对象
        Returns:
            浏览器对象
        """

        return Browser(init_options)
