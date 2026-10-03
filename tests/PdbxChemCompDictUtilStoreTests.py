##
#
# File:    PdbxChemCompDictUtilStoreTests.py
# Date:    29-Sep-2026
#
##
"""
Test cases for PdbxChemCompDictUtil using the bundled chemical component test data.

Store creation and update are exercised end-to-end against the persistent store, while
call sequencing, size checks and failure paths are exercised by mocking the underlying
reader and persistence classes.  Only the public interface of PdbxChemCompDictUtil is used.
"""

import glob
import io
import os
import platform
import shutil
import sys
import tempfile
import unittest
from typing import Any, Callable, Dict, List, Tuple
from unittest import mock

from mmcif.api.DataCategory import DataCategory
from mmcif.api.PdbxContainers import ContainerBase
from mmcif_utils.persist.PdbxCoreIoAdapter import PdbxCoreIoAdapter
from mmcif_utils.persist.PdbxPersist import PdbxPersist

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictUtil import PdbxChemCompDictUtil

UtilCall = Callable[[PdbxChemCompDictUtil], Any]

HERE = os.path.abspath(os.path.dirname(__file__))
TESTOUTPUT = os.path.join(HERE, "test-output", platform.python_version())
DATAINP = os.path.join(HERE, "data", "ligand-dict-v3")

MODPATH = "wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictUtil"


def writeBytes(nBytes: int) -> Callable[..., bool]:
    """Return a PdbxPersist.store() side effect which writes a file of nBytes to dbFileName."""

    def _store(dbFileName: str = "my.db") -> bool:
        with open(dbFileName, "wb") as ofh:
            ofh.write(b"x" * nBytes)
        return True

    return _store


class PdbxChemCompDictUtilStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lfh = sys.stderr
        if not os.path.exists(TESTOUTPUT):  # pragma: no cover
            os.makedirs(TESTOUTPUT)
        self.workDir = tempfile.mkdtemp(dir=TESTOUTPUT)
        self.pathList: List[str] = sorted(glob.glob(os.path.join(DATAINP, "*.cif")))
        self.assertGreaterEqual(len(self.pathList), 3, "test data missing")
        self.ccIdList: List[str] = [os.path.splitext(os.path.basename(pth))[0] for pth in self.pathList]
        self.dictPath = os.path.join(self.workDir, "Components-all-v3.cif")
        with open(self.dictPath, "w", encoding="utf-8") as ofh:
            for pth in self.pathList:
                with open(pth, encoding="utf-8") as ifh:
                    ofh.write(ifh.read())
                ofh.write("\n")
        self.storePath = os.path.join(self.workDir, "chemcomp.db")
        self.tmpStorePath = self.storePath + "-tmpstore"

    def tearDown(self) -> None:
        shutil.rmtree(self.workDir, ignore_errors=True)

    # --------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------

    def getUtil(self, verbose: bool = False) -> PdbxChemCompDictUtil:
        return PdbxChemCompDictUtil(verbose=verbose, log=self.lfh)

    def getStoreContainerNames(self, storePath: str) -> List[str]:
        myPersist = PdbxPersist(False, self.lfh)
        indexD = myPersist.getIndex(dbFileName=storePath)
        return sorted(tup[0] for tup in indexD.get("__containers__", []))

    def readContainers(self, pathList: List[str]) -> List[ContainerBase]:
        myReader = PdbxCoreIoAdapter(False, self.lfh)
        for pth in pathList:
            self.assertTrue(myReader.read(pdbxFilePath=pth))
        return myReader.getContainerList()

    @staticmethod
    def patchReader() -> Any:
        return mock.patch(MODPATH + ".PdbxIoAdapter", autospec=True)

    @staticmethod
    def patchPersist() -> Any:
        return mock.patch(MODPATH + ".PdbxPersist", autospec=True)

    # --------------------------------------------------------------------
    # End-to-end tests using the bundled data
    # --------------------------------------------------------------------

    def testMakeStoreFromFile(self) -> None:
        """Create a store from a concatenated dictionary file."""
        ok = self.getUtil().makeStoreFromFile(dictPath=self.dictPath, storePath=self.storePath)
        self.assertTrue(ok)
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList)
        self.assertFalse(os.path.exists(self.tmpStorePath))

    def testMakeStoreFromFileReplacesExisting(self) -> None:
        """Creating a store over an existing one replaces rather than merges its contents."""
        dUtil = self.getUtil()
        self.assertTrue(dUtil.makeStoreFromFile(dictPath=self.dictPath, storePath=self.storePath))
        self.assertTrue(dUtil.makeStoreFromFile(dictPath=self.pathList[0], storePath=self.storePath))
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList[:1])

    def testMakeStoreFromFileTooSmall(self) -> None:
        """A store smaller than minSize is rejected and not moved into place."""
        ok = self.getUtil().makeStoreFromFile(dictPath=self.dictPath, storePath=self.storePath, minSize=sys.maxsize)
        self.assertFalse(ok)
        self.assertFalse(os.path.exists(self.storePath))

    def testMakeStoreFromPathList(self) -> None:
        """Create a store from a list of individual definition files, verbose logging enabled."""
        log = io.StringIO()
        dUtil = PdbxChemCompDictUtil(verbose=True, log=log)
        ok = dUtil.makeStoreFromPathList(pathList=self.pathList, storePath=self.storePath)
        self.assertTrue(ok)
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList)
        self.assertFalse(os.path.exists(self.tmpStorePath))
        self.assertIn("Read completed for %d definitions" % len(self.pathList), log.getvalue())

    def testMakeStoreFromPathListQuiet(self) -> None:
        """With verbose disabled no progress message is logged."""
        log = io.StringIO()
        dUtil = PdbxChemCompDictUtil(verbose=False, log=log)
        self.assertTrue(dUtil.makeStoreFromPathList(pathList=self.pathList, storePath=self.storePath))
        self.assertNotIn("Read completed", log.getvalue())

    def testUpdateStoreByFile(self) -> None:
        """Create a store from a subset of files, then add the remainder."""
        dUtil = self.getUtil()
        self.assertTrue(dUtil.makeStoreFromPathList(pathList=self.pathList[:2], storePath=self.storePath))
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList[:2])

        ok = dUtil.updateStoreByFile(pathList=self.pathList[2:], storePath=self.storePath)
        self.assertTrue(ok)
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList)

    def testUpdateStoreByFileExisting(self) -> None:
        """Updating with definitions already in the store does not duplicate containers."""
        dUtil = self.getUtil()
        self.assertTrue(dUtil.makeStoreFromPathList(pathList=self.pathList, storePath=self.storePath))
        self.assertTrue(dUtil.updateStoreByFile(pathList=self.pathList[:2], storePath=self.storePath))
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList)

    def testUpdateStoreByObject(self) -> None:
        """Add a new category object to an existing container."""
        dUtil = self.getUtil()
        self.assertTrue(dUtil.makeStoreFromFile(dictPath=self.dictPath, storePath=self.storePath))

        ccId = self.ccIdList[0]
        dObj = DataCategory("test_category", ["id", "value"], [["1", "abc"]])
        ret = dUtil.updateStoreByObject(dObj, containerName=ccId, storePath=self.storePath)
        self.assertIsNot(ret, False)

        myPersist = PdbxPersist(False, self.lfh)
        fObj = myPersist.fetchOneObject(dbFileName=self.storePath, containerName=ccId, objectName="test_category")
        self.assertIsNotNone(fObj)
        assert fObj is not None  # for mypy
        self.assertEqual(fObj.getValue("value", 0), "abc")

        # Other containers are untouched (the expected lookup failure is logged, so capture it)
        oObj = PdbxPersist(False, io.StringIO()).fetchOneObject(
            dbFileName=self.storePath, containerName=self.ccIdList[1], objectName="test_category"
        )
        self.assertIsNone(oObj)

    def testUpdateStoreByContainer(self) -> None:
        """Add containers read from files to an existing store."""
        dUtil = self.getUtil()
        self.assertTrue(dUtil.makeStoreFromPathList(pathList=self.pathList[:1], storePath=self.storePath))

        containerList = self.readContainers(self.pathList[1:])
        ret = dUtil.updateStoreByContainer(containerList=containerList, storePath=self.storePath)
        self.assertIsNot(ret, False)
        self.assertEqual(self.getStoreContainerNames(self.storePath), self.ccIdList)

    # --------------------------------------------------------------------
    # Call sequencing and size checks using mocks
    # --------------------------------------------------------------------

    def testMakeStoreFromFileMocked(self) -> None:
        """The store is written to a temporary path and then moved into place."""
        log = io.StringIO()
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            reader = mockReader.return_value
            reader.read.return_value = True
            reader.getContainerList.return_value = ["c1"]
            persist = mockPersist.return_value
            persist.store.side_effect = writeBytes(100)
            ok = PdbxChemCompDictUtil(verbose=True, log=log).makeStoreFromFile(
                dictPath="in.cif", storePath=self.storePath
            )

        self.assertTrue(ok)
        mockReader.assert_called_once_with(True, log)
        mockPersist.assert_called_once_with(True, log)
        reader.read.assert_called_once_with(pdbxFilePath="in.cif")
        persist.setContainerList.assert_called_once_with(["c1"])
        persist.store.assert_called_once_with(dbFileName=self.tmpStorePath)
        persist.moveStore.assert_called_once_with(self.tmpStorePath, self.storePath)

    def testMakeStoreFromFileSizeBoundary(self) -> None:
        """The temporary store must be strictly larger than minSize to be accepted."""
        for nBytes, expected in ((9, False), (10, False), (11, True)):
            with self.subTest(nBytes=nBytes), self.patchReader(), self.patchPersist() as mockPersist:
                persist = mockPersist.return_value
                persist.store.side_effect = writeBytes(nBytes)
                ok = self.getUtil().makeStoreFromFile(dictPath="in.cif", storePath=self.storePath, minSize=10)
                self.assertEqual(ok, expected)
                self.assertEqual(persist.moveStore.called, expected)

    def testMakeStoreFromFileMissingInput(self) -> None:
        """A missing dictionary file which yields no store fails the size check."""
        missing = os.path.join(self.workDir, "does-not-exist.cif")
        with self.patchPersist() as mockPersist:
            ok = self.getUtil().makeStoreFromFile(dictPath=missing, storePath=self.storePath)
        self.assertFalse(ok)
        mockPersist.return_value.setContainerList.assert_called_once_with([])
        mockPersist.return_value.moveStore.assert_not_called()

    def testMakeStoreFromPathListMocked(self) -> None:
        """Each path is read in order into a single reader and stored in one pass."""
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            reader = mockReader.return_value
            reader.getContainerList.return_value = ["a", "b"]
            persist = mockPersist.return_value
            persist.store.side_effect = writeBytes(100)
            ok = self.getUtil().makeStoreFromPathList(pathList=["a.cif", "b.cif"], storePath=self.storePath)

        self.assertTrue(ok)
        mockReader.assert_called_once()
        self.assertEqual(reader.read.call_args_list, [mock.call(pdbxFilePath="a.cif"), mock.call(pdbxFilePath="b.cif")])
        persist.setContainerList.assert_called_once_with(["a", "b"])
        persist.store.assert_called_once_with(dbFileName=self.tmpStorePath)
        persist.moveStore.assert_called_once_with(self.tmpStorePath, self.storePath)

    def testMakeStoreFromPathListNoStoreWritten(self) -> None:
        """If no temporary store is produced the result is False and nothing is moved."""
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            ok = self.getUtil().makeStoreFromPathList(pathList=["a.cif", "b.cif"], storePath=self.storePath)

        self.assertFalse(ok)
        self.assertEqual(mockReader.return_value.read.call_count, 2)
        mockPersist.return_value.store.assert_called_once_with(dbFileName=self.tmpStorePath)
        mockPersist.return_value.moveStore.assert_not_called()

    def testUpdateStoreByFileMocked(self) -> None:
        """The store is updated with the accumulated reader contents after each file."""
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            reader = mockReader.return_value
            reader.getContainerList.side_effect = [["a"], ["a", "b"]]
            ok = self.getUtil().updateStoreByFile(pathList=["a.cif", "b.cif"], storePath=self.storePath)

        self.assertTrue(ok)
        mockReader.assert_called_once()
        self.assertEqual(reader.read.call_count, 2)
        self.assertEqual(
            mockPersist.return_value.updateContainerList.call_args_list,
            [
                mock.call(dbFileName=self.storePath, containerList=["a"]),
                mock.call(dbFileName=self.storePath, containerList=["a", "b"]),
            ],
        )

    def testUpdateStoreByFileEmpty(self) -> None:
        """An empty path list succeeds without touching the store."""
        with self.patchReader(), self.patchPersist() as mockPersist:
            self.assertTrue(self.getUtil().updateStoreByFile(pathList=[], storePath=self.storePath))
        mockPersist.assert_not_called()

    def testUpdateStoreByObjectMocked(self) -> None:
        """Container name and type are passed through to the persistence layer."""
        dObj = DataCategory("test_category", ["id"], [["1"]])
        with self.patchPersist() as mockPersist:
            ret = self.getUtil().updateStoreByObject(
                dObj, containerName="A", containerType="definition", storePath=self.storePath
            )
        self.assertIsNot(ret, False)
        mockPersist.return_value.updateOneObject.assert_called_once_with(
            dObj, dbFileName=self.storePath, containerName="A", containerType="definition"
        )

    def testUpdateStoreByContainerMocked(self) -> None:
        """The container list is passed through to the persistence layer."""
        with self.patchPersist() as mockPersist:
            ret = self.getUtil().updateStoreByContainer(containerList=["a"], storePath=self.storePath)
        self.assertIsNot(ret, False)
        mockPersist.return_value.updateContainerList.assert_called_once_with(
            dbFileName=self.storePath, containerList=["a"]
        )

    def testDefaultStorePath(self) -> None:
        """Each method defaults to the store path chemcomp.db."""
        dObj = DataCategory("test_category", ["id"], [["1"]])
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            mockReader.return_value.getContainerList.return_value = []
            persist = mockPersist.return_value
            dUtil = self.getUtil()

            # No temporary store is written, so neither create call reaches moveStore()
            dUtil.makeStoreFromFile(dictPath="in.cif")
            dUtil.makeStoreFromPathList(pathList=["a.cif"])
            self.assertEqual(persist.store.call_args_list, [mock.call(dbFileName="chemcomp.db-tmpstore")] * 2)

            dUtil.updateStoreByFile(pathList=["a.cif"])
            dUtil.updateStoreByContainer(containerList=[])
            self.assertEqual(
                persist.updateContainerList.call_args_list,
                [mock.call(dbFileName="chemcomp.db", containerList=[])] * 2,
            )

            dUtil.updateStoreByObject(dObj)
            persist.updateOneObject.assert_called_once_with(
                dObj, dbFileName="chemcomp.db", containerName=None, containerType="data"
            )

    # --------------------------------------------------------------------
    # Failure paths using mocks
    # --------------------------------------------------------------------

    def testReaderException(self) -> None:
        """Exceptions raised constructing the reader are caught and reported as failure."""
        cases: Dict[str, UtilCall] = {
            "makeStoreFromFile": lambda d: d.makeStoreFromFile(dictPath="in.cif", storePath=self.storePath),
            "makeStoreFromPathList": lambda d: d.makeStoreFromPathList(pathList=["a.cif"], storePath=self.storePath),
            "updateStoreByFile": lambda d: d.updateStoreByFile(pathList=["a.cif"], storePath=self.storePath),
        }
        for name, func in cases.items():
            with self.subTest(method=name), mock.patch(MODPATH + ".PdbxIoAdapter", side_effect=RuntimeError("boom")):
                self.assertFalse(func(self.getUtil()))

    def testReadException(self) -> None:
        """Exceptions raised while reading are caught and nothing is stored."""
        with self.patchReader() as mockReader, self.patchPersist() as mockPersist:
            mockReader.return_value.read.side_effect = OSError("unreadable")
            dUtil = self.getUtil()
            self.assertFalse(dUtil.makeStoreFromFile(dictPath="in.cif", storePath=self.storePath))
            self.assertFalse(dUtil.makeStoreFromPathList(pathList=["a.cif"], storePath=self.storePath))
            self.assertFalse(dUtil.updateStoreByFile(pathList=["a.cif"], storePath=self.storePath))
        mockPersist.assert_not_called()

    def testPersistException(self) -> None:
        """Exceptions raised by the persistence layer are caught and reported as failure."""
        dObj = DataCategory("test_category", ["id"], [["1"]])
        cases: Dict[str, Tuple[str, UtilCall]] = {
            "makeStoreFromFile": ("store", lambda d: d.makeStoreFromFile(dictPath="in.cif", storePath=self.storePath)),
            "makeStoreFromPathList": (
                "store",
                lambda d: d.makeStoreFromPathList(pathList=["a.cif"], storePath=self.storePath),
            ),
            "updateStoreByFile": (
                "updateContainerList",
                lambda d: d.updateStoreByFile(pathList=["a.cif"], storePath=self.storePath),
            ),
            "updateStoreByObject": (
                "updateOneObject",
                lambda d: d.updateStoreByObject(dObj, containerName="A", storePath=self.storePath),
            ),
            "updateStoreByContainer": (
                "updateContainerList",
                lambda d: d.updateStoreByContainer(containerList=[], storePath=self.storePath),
            ),
        }
        for name, (persistMethod, func) in cases.items():
            with self.subTest(method=name), self.patchReader(), self.patchPersist() as mockPersist:
                getattr(mockPersist.return_value, persistMethod).side_effect = RuntimeError("boom")
                self.assertFalse(func(self.getUtil()))  # pylint: disable=not-callable
                mockPersist.return_value.moveStore.assert_not_called()

    def testMoveStoreException(self) -> None:
        """A failure moving the temporary store into place is reported as failure."""
        with self.patchReader(), self.patchPersist() as mockPersist:
            persist = mockPersist.return_value
            persist.store.side_effect = writeBytes(100)
            persist.moveStore.side_effect = OSError("cannot move")
            self.assertFalse(self.getUtil().makeStoreFromFile(dictPath="in.cif", storePath=self.storePath))
            self.assertFalse(self.getUtil().makeStoreFromPathList(pathList=["a.cif"], storePath=self.storePath))
        self.assertFalse(os.path.exists(self.storePath))


if __name__ == "__main__":
    unittest.main()
