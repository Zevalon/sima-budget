from enum import StrEnum


class ScopeType(StrEnum):
    OWN = "OWN"
    OWN_UNIT = "OWN_UNIT"
    OWN_UNIT_AND_CHILDREN = "OWN_UNIT_AND_CHILDREN"
    ALL = "ALL"
