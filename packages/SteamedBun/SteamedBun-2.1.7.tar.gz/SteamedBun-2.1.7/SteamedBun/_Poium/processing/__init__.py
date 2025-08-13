"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: __init__.py
@Time: 2023/12/9 18:00
"""

import os
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from SteamedBun import logger

current_path = os.path.abspath(__file__)
BASE_DIR = os.path.abspath(os.path.dirname(current_path) + os.path.sep)


class Cfg:
    # 报告截图路径
    report_snapshot = "."


def compress_image(filename: str):
    """
    不改变图片尺寸压缩到指定大小
    """
    im = Image.open(filename)
    im.save(filename, quality=100)


def screenshots_name(describe=None):
    """
    生成截图的名称, 主要是用于 pytest 用例中
    """
    case_path = os.environ.get('PYTEST_CURRENT_TEST')[:-7]
    this_case_name = case_path.split("/")[-1]
    now_time = int(round(time.time() * 1000))
    tmp_file_name = this_case_name + "::" + str(now_time) + ".jpg"
    print("\n")
    describe = "" if not describe else " => " + describe
    logger.info("截图 📷" + describe + " => " + tmp_file_name)
    snapshot_dir = Cfg.report_snapshot + "/"
    snapshot_name = "{path}{name}".format(path=snapshot_dir, name=tmp_file_name)
    return snapshot_name


def processing(filename: str, image="", text: str = "⊙", color: str = 'red', w=None, h=None, font_size=45):
    """
    点击截图增加水印
    :param filename: 源图片文件
    :param image: 另存为(可选)
    :param text: 水印文案
    :param color: 水印颜色
    :param w: 水印位置 宽 比
    :param h: 水印位置 高 比
    :param font_size: 水印字体大小
    :return:
    """
    font_dir = os.path.join(BASE_DIR, "font/song.ttc")
    font = ImageFont.truetype(font_dir, font_size)
    im1 = Image.open(filename)

    draw = ImageDraw.Draw(im1)
    img_width, img_height = im1.size
    x = img_width * w
    y = img_height * h
    if w is not None and h is not None:
        w = x + font_size / 2
        h = y
    draw.text(xy=(w or x, h or y), text=text, fill=color, font=font, stroke_width=2)  # 设置文字位置/内容/颜色/字体/加粗
    ImageDraw.Draw(im1)  # Just draw it!
    im1.save(image or filename)

    compress_image(filename)
