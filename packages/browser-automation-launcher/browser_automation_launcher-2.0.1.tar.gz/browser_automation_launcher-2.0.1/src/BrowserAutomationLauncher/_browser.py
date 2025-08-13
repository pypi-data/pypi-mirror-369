from dataclasses import dataclass
from os import makedirs, path
from random import randint

from DrissionPage import Chromium, ChromiumOptions


@dataclass
class BrowserWindowLoc:
    width: int = None
    height: int = None
    x: int = None
    y: int = None


class BrowserInitOptions:
    def __init__(self):
        self._browser_path = None
        self._user_data_dirpath = None
        self._port = None

        self._browser_window_loc = None

    def set_basic_options(
        self,
        browser_path: str = None,
        user_data_dirpath: str = None,
        port=9333,
    ):
        """
        设置基础参数

        Args:
            browser_path: 浏览器可执行文件路径
            user_data_dirpath: 用户数据目录路径
            port: 端口号
            auto_close: 是否自动关闭浏览器
        """

        self._browser_path = browser_path
        self._user_data_dirpath = user_data_dirpath
        self._port = port

        return self

    def set_random_port(self, begin=9333, end=999):
        """
        设置随机端口号

        Args:
            begin: 随机端口号起始值
            end: 随机端口号结束值
        """

        self._port = randint(begin, end)

        return self

    def set_window_loc(self, width=1400, height=800, x=20, y=20):
        """
        设置浏览器窗口位置

        Args:
            width: 窗口宽度
            height: 窗口高度
            x: 窗口左上角x坐标
            y: 窗口左上角y坐标
        """

        self._browser_window_loc = BrowserWindowLoc(width, height, x, y)

        return self


class Browser:
    def __init__(self, options: BrowserInitOptions):
        self._options = options
        self._chromium = self.__connect()

    def __connect(self):
        """连接浏览器"""

        option_paths = {
            'local_port': self._options._port,
        }

        browser_path = self._options._browser_path
        if browser_path and isinstance(browser_path, str):
            if not path.exists(browser_path):
                raise FileNotFoundError(f'浏览器执行文件 [{browser_path}] 不存在')
            option_paths['browser_path'] = browser_path

        user_data_dirpath = self._options._user_data_dirpath
        if user_data_dirpath and isinstance(user_data_dirpath, str):
            if not path.exists(user_data_dirpath) or not path.isdir(user_data_dirpath):
                makedirs(user_data_dirpath, exist_ok=True)

            option_paths['user_data_path'] = user_data_dirpath

        option = ChromiumOptions(read_file=False)
        option.set_paths(**option_paths)
        option.set_argument('--disable-background-networking')
        option.set_argument('--hide-crash-restore-bubble')
        option.set_pref('credentials_enable_service', False)

        chromium = Chromium(addr_or_opts=option)
        chromium.set.load_mode.none()

        if isinstance(self._options._browser_window_loc, BrowserWindowLoc):
            latest_tab = chromium.latest_tab
            latest_tab.set.window.size(
                width=self._options._browser_window_loc.width,
                height=self._options._browser_window_loc.height,
            )
            latest_tab.set.window.location(
                x=self._options._browser_window_loc.x,
                y=self._options._browser_window_loc.y,
            )

        return chromium

    @property
    def port(self):
        return self._options._port

    @property
    def chromium(self):
        return self._chromium

    def quit(self):
        """退出浏览器"""

        if not isinstance(self._chromium, Chromium):
            return

        self._chromium.quit(force=True)
