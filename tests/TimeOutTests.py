##
#
# File:    TimeOutTests.py
# Author:  jdw
# Date:    17-Nov-2011
# Version: 0.001
#
# Updates:
#
##
"""
A collection of tests for timeout decorator functions.

"""

import inspect
import sys
import time
import traceback
import unittest

from wwpdb.utils.cc_dict_util.timeout.TimeoutMultiProc import TimeoutException, timeout


class TimeOutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__lfh = sys.stderr

    def tearDown(self) -> None:
        pass

    @timeout(10)
    def longrunner(self, iSeconds: int = 10) -> None:
        self.__lfh.write("SLEEPING FOR %d seconds\n" % iSeconds)
        time.sleep(iSeconds)
        self.__lfh.write("SLEEPING COMPLETED\n")

    # pylint: disable=protected-access
    def testTimeOut1(self) -> None:
        """Test case -"""
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, inspect.currentframe().f_back.f_code.co_name))  # type: ignore[union-attr]
        try:
            self.longrunner(20)
        except TimeoutException:
            self.__lfh.write("Caught timeout exception %s %s\n" % sys.exc_info()[:2])
        except:  # noqa: E722  # pragma: no cover pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()
        else:  # pragma: no cover
            self.__lfh.write("Successful completion\n")
            self.fail()

    # pylint: disable=protected-access
    def testNoTimeOut1(self) -> None:
        """Test case - sleep completes without timeout"""
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, inspect.currentframe().f_back.f_code.co_name))  # type: ignore[union-attr]
        try:
            # Shorter than expected timeout
            self.longrunner(5)
        except TimeoutException:  # pragma: no cover
            # Should not happen
            self.__lfh.write("Caught timeout exception %s %s\n" % sys.exc_info()[:2])
            self.fail()
        except:  # noqa: E722  # pragma: no cover pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()
        else:
            self.__lfh.write("Successful completion\n")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
