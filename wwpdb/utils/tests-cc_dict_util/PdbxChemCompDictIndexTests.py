##
#
# File:    PdbxChemCompDictIndexTests.py
# Author:  J. Westbrook
# Date:    23-Feb-2012
# Version: 0.001
#
# Updates:
#
#  21-Apr-2013  jdw Add test for indexing parent residues --
#   1-Feb-2017  jdw Rename and update in in cc_dict_util package -
##
"""
Test cases for PdbxChemCompIndex demonstrating creation and reading
search indices for chemical component dictionary data.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import unittest
import traceback
import time
import os
import platform

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictIndex import PdbxChemCompDictIndex


# pylint: disable=protected-access
class PdbxChemCompDictIndexTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stdout
        self.__verbose = True
        self.__debug = False
        #
        # Should exist from a previous test case --
        here = os.path.abspath(os.path.dirname(__file__))
        outdir = os.path.join(here, "test-output", platform.python_version())
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.__persistStorePath = os.path.join(outdir, "chemcomp.db")
        self.__indexPath = os.path.join(outdir, "chemcomp-index.pic")
        self.__parentIndexPath = os.path.join(outdir, "chemcomp-parent-index.pic")
        # But if persistStore is not setup, these tests will fail.
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            os.system("python %s/PdbxChemCompPersistTests.py" % here)

    def tearDown(self):
        pass

    def testCreateIndex(self):
        """Test case -  create search index from persistent store"""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            dIndx = PdbxChemCompDictIndex(verbose=self.__verbose, log=self.__lfh)
            dIndx.makeIndex(storePath=self.__persistStorePath, indexPath=self.__indexPath)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testCreateParentIndex(self):
        """Test case -  create search index for parent residues from persistent store"""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            dIndx = PdbxChemCompDictIndex(verbose=self.__verbose, log=self.__lfh)
            pD, cD = dIndx.makeParentComponentIndex(storePath=self.__persistStorePath, indexPath=self.__parentIndexPath)
            self.__lfh.write("+testCreateParentIndex() parent dictionary length %r\n" % len(pD))
            self.__lfh.write("+testCreateParentIndex() child dictionary length %r\n" % len(cD))
            #
            d1, d2 = dIndx.readParentComponentIndex(indexPath=self.__parentIndexPath)
            self.__lfh.write("+testCreateParentIndex() recovered parent dictionary length %r\n" % len(d1))
            self.__lfh.write("+testCreateParentIndex() recovered child dictionary length %r\n" % len(d2))
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testReadIndex(self):
        """Test case -  read search index"""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            dIndx = PdbxChemCompDictIndex(verbose=self.__verbose, log=self.__lfh)
            dIndx.readIndex(indexPath=self.__indexPath)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%.3f seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )


def suiteChemCompBuildIndex():  # pgragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompDictIndexTests("testCreateIndex"))
    suiteSelect.addTest(PdbxChemCompDictIndexTests("testReadIndex"))
    return suiteSelect


def suiteChemCompBuildParentIndex():  # pragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompDictIndexTests("testCreateParentIndex"))
    return suiteSelect


if __name__ == "__main__":  # pragma: no cover
    #
    mySuite2 = suiteChemCompBuildIndex()
    unittest.TextTestRunner(verbosity=2).run(mySuite2)

    mySuite1 = suiteChemCompBuildParentIndex()
    unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
