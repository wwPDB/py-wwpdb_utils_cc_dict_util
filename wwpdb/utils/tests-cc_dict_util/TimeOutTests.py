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
import sys
import unittest
import traceback
import time

from wwpdb.utils.cc_dict_util.timeout.TimeoutMultiProc import timeout, TimeoutException


class TimeOutTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stderr
        self.__verbose = True

    def tearDown(self):
        pass

    @timeout(10)
    def longrunner(self, iSeconds=10):
        self.__lfh.write("SLEEPING FOR %d seconds\n" % iSeconds)
        time.sleep(iSeconds)
        self.__lfh.write("SLEEPING COMPLETED\n")

    # pylint: disable=protected-access
    def testTimeOut1(self):
        """Test case -
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__,
                                                 sys._getframe().f_code.co_name))
        try:
            self.longrunner(20)
        except TimeoutException:
            self.__lfh.write("Caught timeout exception %s %s\n" % sys.exc_info()[:2])
        except:  # noqa: E722; # pragma: no cover pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()
        else:  # pragma: no cover
            self.__lfh.write("Successful completion\n")
            self.fail()

    # pylint: disable=protected-access
    def testNoTimeOut1(self):
        """Test case - sleep completes without timeout
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__,
                                                 sys._getframe().f_code.co_name))
        try:
            # Shorter than expected timeout
            self.longrunner(5)
        except TimeoutException:  # pragma: no cover
            # Should not happen
            self.__lfh.write("Caught timeout exception %s %s\n" % sys.exc_info()[:2])
            self.fail()
        except:  # noqa: E722; # pragma: no cover pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()
        else:
            self.__lfh.write("Successful completion\n")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
