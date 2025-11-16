##
#  File:  TimeoutMultiProc.py
#  Date:  17-Nov-2011  Jdw
#
##

"""
Code to timeout with processes.

>>> @timeout(.5)
... def sleep(x):
...     print "ABOUT TO SLEEP {0} SECONDS".format(x)
...     time.sleep(x)
...     return x

>>> sleep(1)
Traceback (most recent call last):
   ...
TimeoutException: timed out after 0 seconds

>>> sleep(0.2)
0.2

>>> @timeout(0.5)
... def exc():
...     raise Exception("Houston we have problems!")

>>> exc()
Traceback (most recent call last):
   ...
Exception: Houston we have problems!

"""

from __future__ import annotations

import multiprocessing
import signal

# import logging
import sys
import time
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import FrameType

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

# Define ParamSpec for preserving function signature
P = ParamSpec("P")
# Define TypeVar for preserving function return type
R = TypeVar("R")


class TimeoutException(Exception):  # noqa: N818
    def __init__(self, value: str) -> None:
        super(TimeoutException, self).__init__(value)

        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)


class RunableProcessing(multiprocessing.Process):  # pragma: no cover
    def __init__(self, func: Callable[..., None], *args: Any, **kwargs: dict[str, Any]) -> None:
        self.queue: multiprocessing.Queue[Any] = multiprocessing.Queue(maxsize=1)  # pylint: disable=unsubscriptable-object
        args = (func,) + args  # noqa: RUF005
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)
        # logger = multiprocessing.log_to_stderr()
        # logger.setLevel(logging.INFO)

    def run_func(self, func: Callable[..., Any], *args: Any, **kwargs: dict[str, Any]) -> None:
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:  # noqa: BLE001
            self.queue.put((False, e))

    def done(self) -> bool:
        return self.queue.full()

    def result(self) -> Any:
        return self.queue.get()


def timeout(seconds: int, message: str = "Function call timed out") -> Callable[[Callable[P, R]], Callable[P, R]]:
    def wrapper(function: Callable[P, R]) -> Callable[P, R]:
        def _handleTimeout(signum: int, frame: FrameType | None) -> None:  # noqa: ARG001
            raise TimeoutException(message)

        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            signal.signal(signal.SIGALRM, _handleTimeout)
            signal.alarm(seconds)
            try:
                result = function(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapped

    return wrapper


def timeoutMp(seconds: int, force_kill: bool = True) -> Callable[[Callable[..., None]], Callable[P, R]]:  # pragma: no cover
    def wrapper(function: Callable[..., None]) -> Callable[P, R]:
        @wraps(function)
        def inner(*args: P.args, **kwargs: P.kwargs) -> Any:
            now = time.time()
            proc = RunableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = int(time.time() - now)
                exc = f"timed out after {runtime} seconds"
                raise TimeoutException(exc)
            assert proc.done()  # noqa: S101
            success, result = proc.result()
            if success:
                return result
            raise result

        return inner

    return wrapper


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
