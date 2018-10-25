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
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"


import sys, unittest, traceback
import sys, time, os, os.path, shutil
import logging


from wwpdb.utils.cc_dict_util.timeout.TimeoutMultiProc import timeout, TimeoutException

class TimeOutTests(unittest.TestCase):
    def setUp(self):
        self.__lfh=sys.stderr
        self.__verbose=True
        
    def tearDown(self):
        pass

    @timeout(10)
    def longrunner(self,iSeconds=10):
        self.__lfh.write("SLEEPING FOR %d seconds\n" % iSeconds)
        time.sleep(iSeconds)
        self.__lfh.write("SLEEPING COMPLETED\n")        
    def testTimeOut1(self):
        """Test case -  
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__,
                                               sys._getframe().f_code.co_name))
        try:
            self.longrunner(20)
        except TimeoutException:
            self.__lfh.write("Caught timeout exception %s %s\n" % sys.exc_info()[:2])
        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()
        else:
            self.__lfh.write("Successful completion\n")


def suite():
    return unittest.makeSuite(TimeOutTests,'test')

if __name__ == '__main__':
    unittest.main()
