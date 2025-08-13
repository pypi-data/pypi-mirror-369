"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: Config.py
@Time: 2023/12/9 18:00
"""


class BrowserObject:
    # Default browser driver
    driver = None

    # Default playwright page driver
    page = None

    # Adds a border to the action element of the operation
    show = True

    # selenium screenshot path and If you want to use, you need to set your own
    selenium_screenshot_path = None

    # playwright screenshot path and If you want to use, you need to set your own
    playwright_screenshot_path = None
