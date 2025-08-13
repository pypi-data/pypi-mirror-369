"""
author: 馒头
email: neihanshenshou@163.com
"""


class QuoteFormat:

    @staticmethod
    def random_quote(show=False, **kwargs):
        """
        随机 毒鸡汤语录
        """
        from SteamedBun import get
        quote = get(url="https://api.oick.cn/dutang/api.php", show=show, **kwargs).json()
        return quote
