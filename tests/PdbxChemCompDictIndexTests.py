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
#  29-Sep-2026  ep  Use bundled test data, add typing and mocked failure paths
##
"""
Test cases for PdbxChemCompDictIndex demonstrating creation and reading
search indices for chemical component dictionary data.

The persistent store is built from the bundled chemical component test data.
Paths not covered by that data are exercised by mocking the persistence and
iterator classes.
"""

import glob
import io
import os
import pickle
import platform
import shutil
import sys
import tempfile
import unittest
from typing import Any, List
from unittest import mock

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictIndex import PdbxChemCompDictIndex
from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictUtil import PdbxChemCompDictUtil

HERE = os.path.abspath(os.path.dirname(__file__))
TESTOUTPUT = os.path.join(HERE, "test-output", platform.python_version())
DATAINP = os.path.join(HERE, "data", "ligand-dict-v3")

MODPATH = "wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictIndex"


def _makeChemCompRow(**kwargs: Any) -> mock.MagicMock:
    """Return a mock chem_comp row whose getX() methods return the supplied values."""
    row = mock.MagicMock()
    for name, value in kwargs.items():
        getattr(row, name).return_value = value
    return row


class PdbxChemCompDictIndexTests(unittest.TestCase):
    workDir: str
    pathList: List[str]
    ccIdList: List[str]
    storePath: str

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(TESTOUTPUT):  # pragma: no cover
            os.makedirs(TESTOUTPUT)
        cls.workDir = tempfile.mkdtemp(dir=TESTOUTPUT)
        cls.pathList = sorted(glob.glob(os.path.join(DATAINP, "*.cif")))
        cls.ccIdList = [os.path.splitext(os.path.basename(pth))[0] for pth in cls.pathList]
        cls.storePath = os.path.join(cls.workDir, "chemcomp.db")
        dUtil = PdbxChemCompDictUtil(verbose=False, log=sys.stderr)
        if not dUtil.makeStoreFromPathList(pathList=cls.pathList, storePath=cls.storePath):  # pragma: no cover
            raise RuntimeError("Unable to create persistent store %s" % cls.storePath)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.workDir, ignore_errors=True)

    def setUp(self) -> None:
        self.__lfh = io.StringIO()
        self.__outDir = tempfile.mkdtemp(dir=self.workDir)
        self.__indexPath = os.path.join(self.__outDir, "chemcomp-index.pic")
        self.__parentIndexPath = os.path.join(self.__outDir, "chemcomp-parent-index.pic")

    def tearDown(self) -> None:
        shutil.rmtree(self.__outDir, ignore_errors=True)

    def __getIndexer(self, verbose: bool = True) -> PdbxChemCompDictIndex:
        return PdbxChemCompDictIndex(verbose=verbose, log=self.__lfh)

    # --------------------------------------------------------------------
    # Tests using the bundled data
    # --------------------------------------------------------------------

    def testCreateIndex(self) -> None:
        """Create a search index from the persistent store and check its content."""
        ccIdx = self.__getIndexer().makeIndex(storePath=self.storePath, indexPath=self.__indexPath)
        self.assertEqual(sorted(ccIdx.keys()), self.ccIdList)
        self.assertTrue(os.path.exists(self.__indexPath))

        d = ccIdx["ATP"]
        self.assertEqual(d["ccId"], "ATP")
        self.assertEqual(d["name"], "ADENOSINE-5'-TRIPHOSPHATE")
        self.assertEqual(d["type"], "NON-POLYMER")
        self.assertEqual(d["formula"], "C10 H16 N5 O13 P3")
        self.assertEqual(d["formulaWeight"], "507.181")
        self.assertEqual(d["releaseStatus"], "REL")
        self.assertEqual(d["ambiguousFlag"], "N")
        self.assertEqual(d["typeCounts"], {"C": 10, "H": 16, "N": 5, "O": 13, "P": 3})
        self.assertEqual(d["InChIKey"], "ZKHQWZAMYRWXGA-KQYNXXCUSA-N")
        self.assertEqual(d["InChIKey14"], "ZKHQWZAMYRWXGA")
        self.assertTrue(str(d["InChI"]).startswith("InChI=1S/C10H16N5O13P3/"))
        self.assertEqual(d["smiles"], "c1nc(c2c(n1)n(cn2)C3C(C(C(O3)COP(=O)(O)OP(=O)(O)OP(=O)(O)O)O)O)N")
        self.assertEqual(len(d["smilesList"]), 5)
        self.assertIn(d["smiles"], d["smilesList"])
        # Name plus systematic names from pdbx_chem_comp_identifier
        self.assertIn("ADENOSINE-5'-TRIPHOSPHATE", d["nameList"])
        self.assertIn("adenosine 5'-(tetrahydrogen triphosphate)", d["nameList"])
        # Nothing logged on success
        self.assertEqual(self.__lfh.getvalue(), "")

    def testReadIndex(self) -> None:
        """Recover a search index written by makeIndex()."""
        dIndx = self.__getIndexer()
        ccIdx = dIndx.makeIndex(storePath=self.storePath, indexPath=self.__indexPath)
        rIdx = dIndx.readIndex(indexPath=self.__indexPath)
        self.assertEqual(rIdx, ccIdx)

    def testReadIndexMissing(self) -> None:
        """Reading a missing index returns an empty dictionary."""
        self.assertEqual(self.__getIndexer().readIndex(indexPath=self.__indexPath), {})

    def testCreateParentIndex(self) -> None:
        """Create and recover the parent index - the bundled data has no parent components."""
        dIndx = self.__getIndexer()
        pD, cD = dIndx.makeParentComponentIndex(storePath=self.storePath, indexPath=self.__parentIndexPath)
        self.assertEqual(pD, {})
        self.assertEqual(cD, {})
        self.assertTrue(os.path.exists(self.__parentIndexPath))
        self.assertEqual(dIndx.readParentComponentIndex(indexPath=self.__parentIndexPath), ({}, {}))

    def testReadParentIndexMissing(self) -> None:
        """Reading a missing parent index returns empty dictionaries."""
        self.assertEqual(self.__getIndexer().readParentComponentIndex(indexPath=self.__parentIndexPath), ({}, {}))

    # --------------------------------------------------------------------
    # Paths using mocks
    # --------------------------------------------------------------------

    def testCreateIndexSynonymsMocked(self) -> None:
        """Semicolon separated synonyms are split into the name list."""
        row = _makeChemCompRow(
            getName="NAME1",
            getSynonyms="SYN1;SYN2",
            getReleaseStatus="REL",
            getSubComponentList="?",
            getType="NON-POLYMER",
            getFormula="C1",
            getFormulaWeight="12.011",
            getAmbiguousFlag="N",
        )
        with mock.patch(MODPATH + ".PdbxPersist") as mockPersist, mock.patch(
            MODPATH + ".PdbxChemCompIt", return_value=[row]
        ):
            inst = mockPersist.return_value
            inst.getStoreContainerIndex.return_value = ["XYZ"]
            inst.fetchObject.side_effect = lambda containerName, objectName: (  # noqa: ARG005
                mock.sentinel.chemComp if objectName == "chem_comp" else None
            )
            ccIdx = self.__getIndexer().makeIndex(storePath="in.db", indexPath=self.__indexPath)

        inst.open.assert_called_once_with(dbFileName="in.db")
        inst.close.assert_called_once_with()
        self.assertEqual(ccIdx["XYZ"]["nameList"], ["NAME1", "SYN1", "SYN2"])
        self.assertEqual(ccIdx["XYZ"]["typeCounts"], {})
        self.assertEqual(ccIdx["XYZ"]["smilesList"], [])
        with open(self.__indexPath, "rb") as ifh:
            self.assertEqual(pickle.load(ifh), ccIdx)  # noqa: S301

    def testCreateIndexException(self) -> None:
        """Exceptions from the persistence layer are caught and logged."""
        with mock.patch(MODPATH + ".PdbxPersist", side_effect=RuntimeError("boom")):
            ccIdx = self.__getIndexer().makeIndex(storePath="in.db", indexPath=self.__indexPath)
        self.assertEqual(ccIdx, {})
        self.assertIn("index creation failed for in.db", self.__lfh.getvalue())
        self.assertFalse(os.path.exists(self.__indexPath))

    def testCreateIndexExceptionQuiet(self) -> None:
        """Nothing is logged on failure when verbose is disabled."""
        with mock.patch(MODPATH + ".PdbxPersist", side_effect=RuntimeError("boom")):
            ccIdx = self.__getIndexer(verbose=False).makeIndex(storePath="in.db", indexPath=self.__indexPath)
        self.assertEqual(ccIdx, {})
        self.assertEqual(self.__lfh.getvalue(), "")

    def testCreateParentIndexMocked(self) -> None:
        """Parent/child relationships are recorded for single and multiple parents."""
        rows = [
            _makeChemCompRow(getId="MSE", getNstdParentId="MET"),
            _makeChemCompRow(getId="FME", getNstdParentId="MET"),
            _makeChemCompRow(getId="DAB", getNstdParentId="A,B"),
            _makeChemCompRow(getId="LNG", getNstdParentId="LONG"),
            _makeChemCompRow(getId="NOP", getNstdParentId="?"),
            _makeChemCompRow(getId="DOT", getNstdParentId="."),
            _makeChemCompRow(getId="NUL", getNstdParentId=None),
        ]
        dIndx = self.__getIndexer()
        with mock.patch(MODPATH + ".PdbxPersist") as mockPersist, mock.patch(
            MODPATH + ".PdbxChemCompIt", return_value=rows
        ):
            inst = mockPersist.return_value
            inst.getStoreContainerIndex.return_value = ["C1"]
            inst.fetchObject.return_value = mock.sentinel.chemComp
            pD, cD = dIndx.makeParentComponentIndex(storePath="in.db", indexPath=self.__parentIndexPath)

        inst.open.assert_called_once_with(dbFileName="in.db")
        inst.fetchObject.assert_called_once_with(containerName="C1", objectName="chem_comp")
        inst.close.assert_called_once_with()
        self.assertEqual(pD, {"MET": ["MSE", "FME"]})
        self.assertEqual(cD, {"MSE": ["MET"], "FME": ["MET"], "DAB": ["A", "B"]})
        self.assertIn("compId LNG parent compId LONG", self.__lfh.getvalue())
        self.assertEqual(dIndx.readParentComponentIndex(indexPath=self.__parentIndexPath), (pD, cD))

    def testCreateParentIndexException(self) -> None:
        """Exceptions from the persistence layer are caught and logged."""
        with mock.patch(MODPATH + ".PdbxPersist", side_effect=RuntimeError("boom")):
            pD, cD = self.__getIndexer().makeParentComponentIndex(storePath="in.db", indexPath=self.__parentIndexPath)
        self.assertEqual((pD, cD), ({}, {}))
        self.assertIn("parent index creation failed for in.db", self.__lfh.getvalue())
        self.assertFalse(os.path.exists(self.__parentIndexPath))


if __name__ == "__main__":
    unittest.main()
