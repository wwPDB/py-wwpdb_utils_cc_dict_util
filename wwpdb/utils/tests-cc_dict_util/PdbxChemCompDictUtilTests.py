##
# File:    PdbxChemCompDictUtilTests.py
# Author:  J. Westbrook
# Date:    22-Feb-2012
# Version: 0.001
#
# Updates:
#   23-Feb-2012 Add directory path list generator and update example from prd cc data.
#    2-Feb-2017 jdw unified with chem_ref_data
##
"""
Test cases for PdbxChemCompDictUtil demonstrating creation and updating of serialized
chemical component dictionary data.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import unittest
import traceback
import fnmatch
import sys
import time
import os
import os.path

if sys.version_info[0] < 3:
    from io import open as open

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictUtil import PdbxChemCompDictUtil
from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId


# pylint: disable=protected-access
@unittest.skip("Until tests ported")
class PdbxChemCompDictUtilTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stdout
        self.__verbose = True

        self.__siteId = getSiteId(defaultSiteId="WWPDB_DEPLOY_TEST_RU")
        self.__lfh.write("\nTesting with site environment for:  %s\n" % self.__siteId)
        self.__cI = ConfigInfo(self.__siteId)
        self.__ccDictPath = self.__cI.get("SITE_CC_DICT_PATH")
        #
        self.__pathChemCompDictFile = os.path.join(self.__ccDictPath, "Components-all-v3.cif")
        self.__pathList = os.path.join(self.__ccDictPath, "PATHLIST-v3")
        #
        self.__pathChemCompCVS = self.__cI.get("SITE_CC_CVS_PATH")
        self.__pathPrdChemCompCVS = self.__cI.get("SITE_PRDCC_CVS_PATH")

        self.__persistStorePathA = "chemcompA.db"
        self.__persistStorePathB = "chemcompB.db"

    def tearDown(self):
        pass

    def getPathList(self, topPath, pattern="*", excludeDirs=None, recurse=True):
        """Return a list of file paths in the input topPath which satisfy the input search criteria.

        This version does not follow symbolic links.
        """
        if excludeDirs is None:
            excludeDirs = []
        pathList = []
        #
        try:
            names = os.listdir(topPath)
        except os.error:
            return pathList

        # expand pattern
        pattern = pattern or "*"
        patternList = str.split(pattern, ";")

        for name in names:
            fullname = os.path.normpath(os.path.join(topPath, name))
            # check for matching files
            for pat in patternList:
                if fnmatch.fnmatch(name, pat):
                    if os.path.isfile(fullname):
                        pathList.append(fullname)
                        continue
            if recurse:
                # recursively scan directories
                if os.path.isdir(fullname) and not os.path.islink(fullname) and (name not in excludeDirs):
                    pathList.extend(self.getPathList(topPath=fullname, pattern=pattern, excludeDirs=excludeDirs, recurse=recurse))

        return pathList

    def testCreateStoreDict(self):
        """Test case -  read full chemical component dictionary and  create persistent store."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            dUtil = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            dUtil.makeStoreFromFile(dictPath=self.__pathChemCompDictFile, storePath=self.__persistStorePathA)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testCreateStorePathList(self):
        """Test case -  create persistent store from a path list of chemical component defintions.

        Extract the path list from the distributed path list file.
        """
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccPathList = []
            ifh = open(self.__pathList, "r", encoding="utf-8")
            for line in ifh:
                ccPathList.append(line[:-1])
            ifh.close()
            dUtil = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            dUtil.makeStoreFromPathList(pathList=ccPathList, storePath=self.__persistStorePathB)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testCreateStorePathListFS(self):
        """Test case -  create persistent store from a path list of chemical component defintions.

        Extract the path list by searching the file system.
        """
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccPathList = self.getPathList(topPath=self.__pathChemCompCVS, pattern="*.cif", excludeDirs=["CVS", "REMOVED", "FULL"])
            if self.__verbose:
                self.__lfh.write("Pathlist length is %d\n" % len(ccPathList))
            dUtil = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            dUtil.makeStoreFromPathList(pathList=ccPathList, storePath=self.__persistStorePathB)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testUpdateStorePathList(self):
        """Test case -  update persistent store from a path list of chemical component defintions.

        Extract the path list from the distributed path list file.
        """
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccPathList = self.getPathList(topPath=self.__pathPrdChemCompCVS, pattern="*.cif", excludeDirs=["CVS", "REMOVED", "FULL"])
            if self.__verbose:
                self.__lfh.write("Pathlist length is %d\n" % len(ccPathList))
            #
            dUtil = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            dUtil.updateStoreByFile(pathList=ccPathList, storePath=self.__persistStorePathB)
            #
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )


def suiteChemCompBuildStore():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompDictUtilTests("testCreateStorePathListFS"))
    suiteSelect.addTest(PdbxChemCompDictUtilTests("testCreateStorePathList"))
    suiteSelect.addTest(PdbxChemCompDictUtilTests("testCreateStoreDict"))
    return suiteSelect


def suiteChemCompUpdateStore():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompDictUtilTests("testUpdateStorePathList"))
    return suiteSelect


if __name__ == "__main__":
    #
    if not os.access("chemcompA.db", os.F_OK):
        mySuite1 = suiteChemCompBuildStore()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)

    mySuite2 = suiteChemCompUpdateStore()
    unittest.TextTestRunner(verbosity=2).run(mySuite2)

    #
