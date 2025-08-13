# browser-automation-launcher
浏览器自动化启动器. 与 [DrissionPage](https://pypi.org/project/DrissionPage/) 配合使用, 实现浏览器自动化的启动和关闭.

## 主要功能
- 自动启动浏览器并设置浏览器参数, 例如调试端口号等 (需要指定 Chrome 浏览器的路径)
- 通过端口号接管当前已打开的 Chrome 浏览器 (只能接管通过调试模式打开的浏览器)
- 自动创建或加载浏览器用户数据目录

## 安装
```bash
pip install browser-automation-launcher
```

## 使用方法
```python
from BrowserAutomationLauncher import BrowserInitOptions, Launcher

launcher = Launcher()

init_options = BrowserInitOptions()
init_options.set_basic_options(
    browser_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
)
# 设置浏览器窗口大小 (可选)
init_options.set_window_loc(width=1400, height=900, x=20, y=20)

browser = launcher.init_browser(init_options)
page = browser.chromium.latest_tab

page.get('https://www.baidu.com')
```