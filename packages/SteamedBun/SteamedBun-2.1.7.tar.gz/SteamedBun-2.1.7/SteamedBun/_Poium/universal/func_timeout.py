"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: func_timeout
@Time: 2025/6/29 17:20
"""

import functools
import threading

from SteamedBun._Poium.universal.exceptions import FuncTimeoutException


def func_timeout(timeout):
    """
    A decorator to limit the execution time of a function.
    If the function's execution time exceeds the `timeout` seconds, a `FuncTimeoutException` exception will be raised.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exceptions = [None]

            def target():
                nonlocal result, exceptions
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exceptions[0] = e

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                raise FuncTimeoutException(f"Function {func.__name__} timed out after {timeout} seconds")

            if exceptions[0]:
                raise exceptions[0]

            return result[0]

        return wrapper

    return decorator
