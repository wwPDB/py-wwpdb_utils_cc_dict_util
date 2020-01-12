##
# File: PdbxChemCompConstants.py
# Date: 21-Feb-2012  John Westbrook
#
# Update:
#  21-Feb-2012 jdw add to chemcomputil repository
#   1-Feb-2017 jdw unified with chem_ref_data
#
##
"""
A collection of chemical data and information.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


class PdbxChemCompConstants(object):
    _periodicTable = [
        "H", "HE",
        "LI", "BE", "B", "C", "N", "O", "F", "NE",
        "NA", "MG", "AL", "SI", "P", "S", "CL", "AR",
        "K", "CA", "SC", "TI", "V", "CR", "MN", "FE", "CO", "NI",
        "CU", "ZN", "GA", "GE", "AS", "SE", "BR", "KR",
        "RB", "SR", "Y", "ZR", "NB", "MO", "TC", "RU", "RH", "PD",
        "AG", "CD", "IN", "SN", "SB", "TE", "I", "XE",
        "CS", "BA", "LA", "CE", "PR", "ND", "PM", "SM", "EU", "GD", "TB",
        "DY", "HO", "ER", "TM", "YB", "LU", "HF", "TA", "W",
        "RE", "OS", "IR", "PT", "AU", "HG", "TL", "PB", "BI",
        "PO", "AT", "RN",
        "FR", "RA", "AC", "TH", "PA", "U", "NP", "PU", "AM", "CM", "BK",
        "CF", "ES", "FM", "MD", "NO", "LR", "UNQ", "UNP", "UNH",
        "UNS", "UNO", "UNE"]