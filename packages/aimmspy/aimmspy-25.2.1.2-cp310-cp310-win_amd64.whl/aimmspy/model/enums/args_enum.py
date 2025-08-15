from enum import Enum

class ArgsEnum(Enum):
    """
    Enum for argument types in AIMMS API.
    """
    Input           = 0x00000010
    Output          = 0x00000020
    Input_Output    = 0x00000040
    Optional        = 0x00000080