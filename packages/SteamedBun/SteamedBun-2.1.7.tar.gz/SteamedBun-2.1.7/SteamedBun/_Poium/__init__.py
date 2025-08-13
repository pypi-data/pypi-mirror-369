"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: __init__.py
@Time: 2023/12/9 18:00
"""

from . import playwright
from .config import BrowserObject
from .javascript import CSSElement
from .playwright import Locator
from .playwright import Locators
from .processing import compress_image
from .processing import processing
from .selenium import Element
from .selenium import Elements
from .webdriver import Page
