##
#
# File:    PdbxChemCompPersistTests.py
# Author:  J. Westbrook
# Date:    20-Feb-2012
# Version: 0.001
##
"""
Test cases for PdbxChemCompPersist module applied to chemical component definition data.  This
includes examples of serializing chemical dictionaries, accessor methods for the persistent
data,  derivative indexing created from the persistent store, and search examples using the
the derivative indices.

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
import os.path
import platform
import string
import glob

if sys.version_info[0] < 3:
    from io import open as open

try:
    import cPickle as pickle
except ImportError:
    import pickle

from mmcif_utils.persist.PdbxPersist import PdbxPersist
from mmcif.io.IoAdapterCore import IoAdapterCore as PdbxIoAdapter
from wwpdb.utils.cc_dict_util.persist.PdbxChemCompPersist import PdbxChemCompIt, PdbxChemCompAtomIt, PdbxChemCompDescriptorIt, PdbxChemCompIdentifierIt


# pylint: disable=protected-access
class PdbxChemCompPersistTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stderr
        self.__verbose = True
        self.__debug = False
        HERE = os.path.abspath(os.path.dirname(__file__))
        TESTOUTPUT = os.path.join(HERE, "test-output", platform.python_version())
        if not os.path.exists(TESTOUTPUT):  # pragma: no cover
            os.makedirs(TESTOUTPUT)
        DATAINP = os.path.join(HERE, "data", "ligand-dict-v3")
        self.__pathChemCompDictFile = os.path.join(TESTOUTPUT, "Components-all-v3.cif")
        self.__pathList = os.path.join(TESTOUTPUT, "PATHLIST-v3")
        self.__persistStorePath = os.path.join(TESTOUTPUT, "chemcomp.db")
        self.__indexPath = os.path.join(TESTOUTPUT, "chemcomp-index.pic")
        self.__createFiles(DATAINP, self.__pathChemCompDictFile, self.__pathList)

    def __createFiles(self, source, combined, pathlist):
        # Get list of files
        entlist = glob.glob(source + "/*.cif")

        # Pathlist creation
        with open(pathlist, "w", encoding="utf-8") as fout:
            for ent in entlist:
                if sys.version_info[0] < 3:
                    fout.write((ent + "\n").decode("utf-8"))
                else:
                    fout.write(ent + "\n")

        # Combined file
        with open(combined, "w", encoding="utf-8") as fout:
            for ent in entlist:
                with open(ent, "r", encoding="utf-8") as fin:
                    fout.write(fin.read())
                if sys.version_info[0] < 3:
                    fout.write(("\n").decode("utf-8"))
                else:
                    fout.write("\n")

    def tearDown(self):
        pass

    def testChemCompReadDictionary(self):
        """Test case -  read chemical component dictionary."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
            cList = myReader.readFile(inputFilePath=self.__pathChemCompDictFile)
            self.__lfh.write("Dictionary data block length  = %r\n" % len(cList))
        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompCreateStore(self):
        """Test case -  read chemical component dictionary and  create persistent store."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
            cList = myReader.readFile(inputFilePath=self.__pathChemCompDictFile)
            #
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.setContainerList(cList)
            myPersist.store(dbFileName=self.__persistStorePath)
            #
            # indexD=myPersist.getIndex(dbFileName=self.__persistStorePath)
            # self.__lfh.write("Persistent index dictionary %r\n" % indexD.items())
        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompUpdateStoreByObject(self):
        """Test case -  update persistent store with replacement data by object."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))

        if not os.path.exists(self.__persistStorePath):  # pragma: no cover

            self.testChemCompCreateStore()
        try:
            replacePathList = []
            ifh = open(self.__pathList, "r", encoding="utf-8")
            for line in ifh:
                replacePathList.append(line[:-1])
            ifh.close()
            #
            for rPath in replacePathList[:10]:
                myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
                cList = myReader.readFile(inputFilePath=rPath)
                for container in cList:
                    containerName = container.getName()
                    for objName in container.getObjNameList():
                        myObj = container.getObj(objName)
                        myPersist = PdbxPersist(self.__verbose, self.__lfh)
                        myPersist.updateOneObject(myObj, dbFileName=self.__persistStorePath, containerName=containerName)
        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompUpdateStoreByContainer(self):
        """Test case -  update persistent store with replacement data by container."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))

        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        try:
            replacePathList = []
            ifh = open(self.__pathList, "r", encoding="utf-8")
            for line in ifh:
                replacePathList.append(line[:-1])
            ifh.close()
            #
            for rPath in replacePathList[:10]:
                myReader = PdbxIoAdapter(self.__verbose, self.__lfh)
                cList = myReader.readFile(inputFilePath=rPath)
                myPersist = PdbxPersist(self.__verbose, self.__lfh)
                myPersist.updateContainerList(dbFileName=self.__persistStorePath, containerList=cList)
        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompGetDictionaryIndex(self):
        """Test case - recover index from persistent store"""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)
            self.__lfh.write("Persistent index dictionary length %r\n" % len(indexD))
        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompFetchStatus(self):
        """Test case -  read component dictionary index and fetch release status value from each chem_comp category"""
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)

            myPersist.open(dbFileName=self.__persistStorePath)
            sD = {}
            for ccId, _ccType in indexD["__containers__"]:
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp")
                sV = dC.getValue("pdbx_release_status", 0)
                if sV not in sD:
                    sD[sV] = 1
                else:
                    sD[sV] += 1
            self.__lfh.write("Status count length %r\n" % len(sD))

            myPersist.close()

        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def __cnvChemCompFormulaToElementCounts(self, fS):
        """Convert formula format from chemical component definition to an element count dictionary."""
        eD = {}
        fL = fS.split()
        for f in fL:
            el = ""
            cnt = ""
            for ch in f:
                if ch in string.ascii_letters:
                    el += ch
                elif ch in string.digits:
                    cnt += ch
            if len(cnt) > 0:
                eD[el.upper()] = int(cnt)
            else:
                eD[el.upper()] = 1
        return eD

    def testChemCompInterpretFormula(self):
        """Test case -  read component dictionary index and fetch release status value from each chem_comp category"""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)

            myPersist.open(dbFileName=self.__persistStorePath)
            for ccId, _ccType in indexD["__containers__"]:
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp")
                fS = dC.getValue("formula", 0)
                _d = self.__cnvChemCompFormulaToElementCounts(fS)  # noqa: F841
                # self.__lfh.write("Element counts %s %s ||  %r\n" % (ccId, fS, d.items()))

            myPersist.close()

        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompFetchAtoms(self):
        """Test case -  read component dictionary index and fetch all chem_comp categories"""
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)
            tCount = {}
            myPersist.open(dbFileName=self.__persistStorePath)
            first = True
            for ccId, _ccType in indexD["__containers__"]:
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp_atom")
                if dC is None:
                    continue
                #
                atomIt = PdbxChemCompAtomIt(dC, self.__verbose, self.__lfh)
                for atom in atomIt:
                    # atom.dump(self.__lfh)
                    aType = atom.getType()
                    if atom.getType() not in tCount:
                        tCount[aType] = 1
                    else:
                        tCount[aType] += 1
                    if first:
                        atom.dump(self.__lfh)
                        first = False
                    self.assertNotEqual(atom.getAtNo(), 0)
                    isotope = atom.getIsotope()
                    self.assertTrue(isotope <= 3 and isotope >= 0)

            myPersist.close()
            self.__lfh.write("Type count length: %r\n" % len(tCount))

        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompCompareDescriptors(self):
        """Test case -  read component dictionary index and compare all descriptors."""
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)
            # tCount = {}
            myPersist.open(dbFileName=self.__persistStorePath)
            for ccId, _ccType in indexD["__containers__"]:
                dC = myPersist.fetchObject(containerName=ccId, objectName="pdbx_chem_comp_descriptor")
                if dC is None:
                    continue
                #
                dIt = PdbxChemCompDescriptorIt(dC, self.__verbose, self.__lfh)
                for dA in dIt:
                    desA = dA.getDescriptor()
                    desTypeA = dA.getType()
                    for dB in dIt:
                        desB = dB.getDescriptor()
                        desTypeB = dB.getType()
                        if desTypeA == desTypeB:
                            self.__lfh.write("Id %s %s %s ||| %s %s\n" % (ccId, desA, desTypeA, desB, desTypeB))

            myPersist.close()

        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompMakeSearchIndex(self):
        """Test case -  read component dictionary index and build a search index."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        if not os.path.exists(self.__persistStorePath):  # pragma: no cover
            self.testChemCompCreateStore()
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            indexD = myPersist.getIndex(dbFileName=self.__persistStorePath)
            ccIdx = {}
            myPersist.open(dbFileName=self.__persistStorePath)
            for ccId, _ccType in indexD["__containers__"]:
                #
                d = {}
                d["nameList"] = []
                d["typeCounts"] = {}
                d["InChI"] = None
                d["InChIKey"] = None
                d["smiles"] = None
                d["smilesStereo"] = None
                d["releaseStatus"] = None
                d["subcomponentList"] = None
                #
                #
                nameList = []
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp")
                if dC is not None:
                    rowIt = PdbxChemCompIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        name = row.getName()
                        synonyms = row.getSynonyms()
                        d["releaseStatus"] = row.getReleaseStatus()
                        d["subcomponentList"] = row.getSubComponentList()

                    nameList.append(name)
                    if ";" in synonyms:
                        sList = synonyms.split(";")
                        nameList.extend(sList)
                    else:
                        nameList.append(synonyms)

                # Compute element/type counts directly from the definition atom list
                typeCounts = {}
                dC = myPersist.fetchObject(containerName=ccId, objectName="chem_comp_atom")
                if dC is not None:
                    rowIt = PdbxChemCompAtomIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        aType = row.getType()
                        if row.getType() not in typeCounts:
                            typeCounts[aType] = 1
                        else:
                            typeCounts[aType] += 1
                    d["typeCounts"] = typeCounts

                #
                dC = myPersist.fetchObject(containerName=ccId, objectName="pdbx_chem_comp_descriptor")
                if dC is not None:
                    rowIt = PdbxChemCompDescriptorIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        des = row.getDescriptor()
                        desType = row.getType()
                        desProgram = row.getProgram()
                        if "OpenEye" in desProgram:
                            if desType == "SMILES_CANNONICAL":
                                d["smilesStereo"] = des
                            elif desType == "SMILES":
                                d["smilesStereo"] = des
                        elif "InChI" in desProgram:
                            if desType == "InChI":
                                d["InChI"] = des
                            elif desType == "InChIKey":
                                d["InChIKey"] = des
                #

                dC = myPersist.fetchObject(containerName=ccId, objectName="pdbx_chem_comp_identifier")
                if dC is not None:
                    rowIt = PdbxChemCompIdentifierIt(dC, self.__verbose, self.__lfh)
                    for row in rowIt:
                        iden = row.getIdentifier()
                        idenType = row.getType()
                        _idenProgram = row.getProgram()  # noqa: F841
                        if "SYSTEMATIC" in idenType:
                            nameList.append(iden)

                d["nameList"] = nameList
                ccIdx[ccId] = d

            myPersist.close()
            with open(self.__indexPath, "wb") as fout:
                pickle.dump(ccIdx, fout)

        except:  # noqa: E722 pylint: disable=bare-except  # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )

    def testChemCompSearchIndex(self):
        """Test case -  read component index and test formula filters."""
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            # A few target formulas to test search --
            #
            targetD = {"t1": {"C": 16, "O": 2}, "t2": {"C": 14, "O": 4}, "t3": {"C": 12, "N": 1, "Cl": 2}}
            #
            # upper and lower bounds about the target formula.
            offsetU = 2
            offsetL = 2
            #
            with open(self.__indexPath, "rb") as fin:
                ccIdx = pickle.load(fin)
            #
            for tId, tf in targetD.items():
                mList = []
                for ccId, d in ccIdx.items():
                    refC = d["typeCounts"]
                    #
                    mOk = True
                    for ftype, cnt in tf.items():
                        typeU = ftype.upper()
                        if typeU in refC:
                            if (cnt < refC[typeU] - offsetL) or (cnt > refC[typeU] + offsetU):
                                mOk = False
                                break
                        else:
                            mOk = False
                            break
                    if mOk:
                        if self.__debug:  # pragma: no cover
                            self.__lfh.write("Match %s target %r reference %s %r\n" % (tId, tf, ccId, refC))
                        mList.append(ccId)

                self.__lfh.write("Match list for %s length %r\n" % (tId, len(mList)))

        except:  # noqa: E722 pylint: disable=bare-except;   # pragma: no cover
            traceback.print_exc(file=self.__lfh)
            self.fail()

        endTime = time.time()
        self.__lfh.write(
            "\nCompleted %s %s at %s (%d seconds)\n"
            % (self.__class__.__name__, sys._getframe().f_code.co_name, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)
        )


def suiteChemCompBuildStore():  # pragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompReadDictionary"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompCreateStore"))
    return suiteSelect


def suiteChemCompIndex():  # pragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompGetDictionaryIndex"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompFetchStatus"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompFetchAtoms"))
    # suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompCompareDescriptors"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompInterpretFormula"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompMakeSearchIndex"))
    return suiteSelect


def suiteChemCompSearchIndex():  # pragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompSearchIndex"))
    return suiteSelect


def suiteChemCompUpdate():  # pragma: no cover
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompUpdateStoreByObject"))
    suiteSelect.addTest(PdbxChemCompPersistTests("testChemCompUpdateStoreByContainer"))
    return suiteSelect


if __name__ == "__main__":  # pragma: no cover
    # Run all tests --
    # unittest.main()
    #
    if not os.access("chemcomp.db", os.F_OK):
        mySuite1 = suiteChemCompBuildStore()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
    if not os.access("chemcomp-index.pic", os.F_OK):
        mySuite2 = suiteChemCompIndex()
        unittest.TextTestRunner(verbosity=2).run(mySuite2)
    #
    mySuite3 = suiteChemCompSearchIndex()
    unittest.TextTestRunner(verbosity=2).run(mySuite3)
    #
    mySuite4 = suiteChemCompUpdate()
    unittest.TextTestRunner(verbosity=2).run(mySuite4)
