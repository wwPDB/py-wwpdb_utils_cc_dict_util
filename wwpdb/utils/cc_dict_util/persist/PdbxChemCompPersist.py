##
# File: PdbxChemCompPersist.py
# Date: 20-Feb-2012  John Westbrook
#
# Update:
#  21-Feb-2012 jdw adapted for chemcomputil repository
#  23-Feb-2012 jdw adapted for cc_dict_util repository
#   1-Feb-2017 jdw update imports to pdbx_v2
##
"""
A collection of access and iterator classes supporting chemical component dictionary data
extracted from persistent store.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
from typing import Callable, Generic, Iterator, List, Optional, TextIO, Tuple, TypeVar, Union

from mmcif.api.DataCategory import DataCategory
from typing_extensions import Self

# import traceback
from wwpdb.utils.cc_dict_util.persist.PdbxChemCompConstants import PdbxChemCompConstants

T = TypeVar("T")


class PdbxCategoryItBase(Generic[T]):
    """Base category iterator class."""

    def __init__(
        self,
        dataCategory: DataCategory,
        func: Callable[[List[str]], T],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        self.__rL: List[List[str]] = dataCategory.getRowList()
        self.__func = func

    def get(self, index: int = 0) -> List[str]:
        try:
            return self.__rL[index]
        except:  # noqa: E722 pylint: disable=bare-except
            return []

    def __iter__(self) -> Iterator[T]:
        return self.forward()

    def forward(self) -> Iterator[T]:
        # Forward generator
        current_row = 0
        while current_row < len(self.__rL):
            row = self.__rL[current_row]
            current_row += 1
            yield self.__func(row)

    def reverse(self) -> Iterator[T]:
        # The reverse generator
        current_row = len(self.__rL)
        while current_row > 0:
            current_row -= 1
            yield self.__func(self.__rL[current_row])


class PdbxChemCompIt(PdbxCategoryItBase["PdbxChemCompPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompAtomIt(PdbxCategoryItBase["PdbxChemCompAtomPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompAtomPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompAtomIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompBondIt(PdbxCategoryItBase["PdbxChemCompBondPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompBondPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompBondIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompDescriptorIt(PdbxCategoryItBase["PdbxChemCompDescriptorPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompDescriptorPersist(
            [], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log
        )
        super(PdbxChemCompDescriptorIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompIdentifierIt(PdbxCategoryItBase["PdbxChemCompIdentifierPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompIdentifierPersist(
            [], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log
        )
        super(PdbxChemCompIdentifierIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompAuditIt(PdbxCategoryItBase["PdbxChemCompAuditPersist"]):
    def __init__(self, dataCategory: DataCategory, verbose: bool = True, log: TextIO = sys.stderr) -> None:
        o = PdbxChemCompAuditPersist([], attributeNameList=dataCategory.getAttributeList(), verbose=verbose, log=log)
        super(PdbxChemCompAuditIt, self).__init__(dataCategory, o.set, verbose, log)


class PdbxChemCompPersist:
    """Accessor methods chemical component attributes."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getId(self) -> Optional[str]:
        return self.__getAttribute("id")

    def getName(self) -> Optional[str]:
        return self.__getAttribute("name")

    def getType(self) -> Optional[str]:
        return self.__getAttribute("type")

    def getPdbxType(self) -> Optional[str]:
        return self.__getAttribute("pdbx_type")

    def getFormula(self) -> Optional[str]:
        return self.__getAttribute("formula")

    def getSynonyms(self) -> Optional[str]:
        return self.__getAttribute("pdbx_synonyms")

    def getFormalCharge(self) -> Optional[str]:
        return self.__getAttribute("pdbx_formal_charge")

    def getModificationDate(self) -> Optional[str]:
        return self.__getAttribute("pdbx_modified_date")

    def getInitialDate(self) -> Optional[str]:
        return self.__getAttribute("pdbx_initial_date")

    def getReleaseStatus(self) -> Optional[str]:
        return self.__getAttribute("pdbx_release_status")

    def getFormulaWeight(self) -> Optional[str]:
        return self.__getAttribute("formula_weight")

    def getSubComponentList(self) -> Optional[str]:
        return self.__getAttribute("pdbx_subcomponent_list")

    def getAmbiguousFlag(self) -> Optional[str]:
        return self.__getAttribute("pdbx_ambiguous_flag")

    def getProcessingSite(self) -> Optional[str]:
        return self.__getAttribute("pdbx_processing_site")

    def getReplacesId(self) -> Optional[str]:
        return self.__getAttribute("pdbx_replaces")

    def getReplacesById(self) -> Optional[str]:
        return self.__getAttribute("pdbx_replaced_by")

    def getNstdParentId(self) -> Optional[str]:
        return self.__getAttribute("mon_nstd_parent_comp_id")

    def getOneLetterCode(self) -> Optional[str]:
        return self.__getAttribute("one_letter_code")

    def getThreeLetterCode(self) -> Optional[str]:
        return self.__getAttribute("three_letter_code")

    def getModelCoordinatesPdbCode(self) -> Optional[str]:
        return self.__getAttribute("pdbx_model_coordinates_db_code")

    def getMissingModelCoordinates(self) -> Optional[str]:
        return self.__getAttribute("pdbx_model_coordinates_missing_flag")

    def getMissingIdealCoordinates(self) -> Optional[str]:
        return self.__getAttribute("pdbx_ideal_coordinates_missing_flag")


class PdbxChemCompAtomPersist(PdbxChemCompConstants):
    """Accessor methods chemical component atom attributes."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        super(PdbxChemCompAtomPersist, self).__init__()
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def getName(self) -> Optional[str]:
        return self.__getAttribute("atom_id")

    def isChiral(self) -> bool:
        return self.__getAttribute("pdbx_stereo_config") != "N"

    def getType(self) -> Optional[str]:
        return self.__getAttribute("type_symbol")

    def getLeavingAtomFlag(self) -> Optional[str]:
        return self.__getAttribute("pdbx_leaving_atom_flag")

    def getAtNo(self) -> int:
        try:
            tyU = str(self.getType()).upper()
            if (tyU == "D") or (tyU == "T"):  # noqa: PLR1714
                tyU = "H"
            return self._periodicTable.index(tyU) + 1
        except:  # noqa: E722 pylint: disable=bare-except
            # traceback.print_exc(file=self.__lfh)
            return 0

    def getIsotope(self) -> int:
        ty = self.getType()
        if ty == "D":
            return 2
        if ty == "T":
            return 3
        return 0

    def isAromatic(self) -> bool:
        return self.__getAttribute("pdbx_aromatic_flag") != "N"

    def getCIPStereo(self) -> Optional[str]:
        return self.__getAttribute("pdbx_stereo_config")

    def getFormalCharge(self) -> int:
        try:
            return int(self.__getAttribute("charge"))  # type: ignore
        except:  # noqa: E722 pylint: disable=bare-except
            return 0

    def hasModelCoordinates(self) -> bool:
        x, y, z = self.getModelCoordinates()
        # x=self.__getAttribute('model_Cartn_x')
        # y=self.__getAttribute('model_Cartn_y')
        # z=self.__getAttribute('model_Cartn_z')
        #
        return (x is not None) and (y is not None) and (z is not None)

    def hasIdealCoordinates(self) -> bool:
        x, y, z = self.getIdealCoordinates()
        # x=self.__getAttribute('pdbx_model_Cartn_x_ideal')
        # y=self.__getAttribute('pdbx_model_Cartn_y_ideal')
        # z=self.__getAttribute('pdbx_model_Cartn_z_ideal')
        #
        return (x is not None) and (y is not None) and (z is not None)

    def getModelCoordinates(self) -> Union[Tuple[None, None, None], Tuple[float, float, float]]:
        """Returns (x,y,z)"""
        try:
            x = float(self.__getAttribute("model_Cartn_x"))  # type: ignore
            y = float(self.__getAttribute("model_Cartn_y"))  # type: ignore
            z = float(self.__getAttribute("model_Cartn_z"))  # type: ignore
            return (x, y, z)
        except:  # noqa: E722 pylint: disable=bare-except
            return (None, None, None)

    def getIdealCoordinates(self) -> Union[Tuple[None, None, None], Tuple[float, float, float]]:
        """Returns (x,y,z)"""
        try:
            x = float(self.__getAttribute("pdbx_model_Cartn_x_ideal"))  # type: ignore
            y = float(self.__getAttribute("pdbx_model_Cartn_y_ideal"))  # type: ignore
            z = float(self.__getAttribute("pdbx_model_Cartn_z_ideal"))  # type: ignore
            return (x, y, z)
        except:  # noqa: E722 pylint: disable=bare-except
            return (None, None, None)

    def dump(self, ofh: TextIO) -> None:
        ofh.write("PdbxChemCompAtomPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompBondPersist:
    """Accessor methods chemical component bond attributes."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def getBond(self) -> Tuple[Optional[str], Optional[str]]:
        """Returns (atomI,atomJ) atom ids from the atom list."""
        return (self.__getAttribute("atom_id_1"), self.__getAttribute("atom_id_2"))

    def getType(self) -> Optional[str]:
        return self.__getAttribute("value_order")

    def getIntegerType(self) -> int:
        bT = self.__getAttribute("value_order")
        if bT == "SING":
            return 1
        if bT == "DOUB":
            return 2
        if bT == "TRIP":
            return 3
        if bT == "QUAD":
            return 4
        return 0

    def isAromatic(self) -> bool:
        return self.__getAttribute("pdbx_aromatic_flag") == "Y"

    def getStereo(self) -> Optional[str]:
        return self.__getAttribute("pdbx_stereo_config")

    def hasStereo(self) -> bool:
        return self.__getAttribute("pdbx_stereo_config") != "N"

    def dump(self, ofh: TextIO) -> None:
        ofh.write("PdbxChemCompBondPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompIdentifierPersist:
    """Accessor methods chemical component identifier attributes."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore[index]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def getIdentifier(self) -> Optional[str]:
        """Returns the value of the identifier."""
        return self.__getAttribute("identifier")

    def getType(self) -> Optional[str]:
        return self.__getAttribute("type")

    def getProgram(self) -> Optional[str]:
        return self.__getAttribute("program")

    def getProgramVersion(self) -> Optional[str]:
        return self.__getAttribute("program_version")

    def dump(self, ofh: TextIO) -> None:
        ofh.write("PdbxChemCompIdentifierPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompDescriptorPersist:
    """Accessor methods chemical component descriptor  attributes."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:  # noqa: ARG002 pylint: disable=unused-argument
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore[index]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def getDescriptor(self) -> Optional[str]:
        """Returns the value of the descriptor."""
        return self.__getAttribute("descriptor")

    def getType(self) -> Optional[str]:
        return self.__getAttribute("type")

    def getProgram(self) -> Optional[str]:
        return self.__getAttribute("program")

    def getProgramVersion(self) -> Optional[str]:
        return self.__getAttribute("program_version")

    def dump(self, ofh: TextIO) -> None:
        ofh.write("PdbxChemCompDescriptorPersist(dump) %r\n" % self.__rowData)


class PdbxChemCompAuditPersist:
    """Accessor methods chemical component audit details."""

    def __init__(
        self,
        rowData: Optional[List[str]],
        attributeNameList: List[str],
        verbose: bool = True,  # noqa: ARG002 pylint: disable=unused-argument
        log: TextIO = sys.stderr,  # noqa: ARG002 pylint: disable=unused-argument
    ) -> None:
        self.__rowData = rowData
        self.__attributeNameList = attributeNameList

    def __getAttribute(self, name: str) -> Optional[str]:
        try:
            i = self.__attributeNameList.index(name)
            return self.__rowData[i]  # type: ignore
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def set(self, rowData: Optional[List[str]] = None) -> Self:
        self.__rowData = rowData
        return self

    def getActionType(self) -> Optional[str]:
        """Returns the value of the action type."""
        return self.__getAttribute("action_type")

    def getDate(self) -> Optional[str]:
        """Returns the value of audit date."""
        return self.__getAttribute("date")

    def getProcessingSite(self) -> Optional[str]:
        """Returns the value of processing site."""
        return self.__getAttribute("processing_site")

    def getAnnotator(self) -> Optional[str]:
        """Returns the value of audit annotator."""
        return self.__getAttribute("annotator")

    def getDetails(self) -> Optional[str]:
        """Returns the value of audit details."""
        return self.__getAttribute("details")
