from enum import Enum


from enum import Enum

class Flag(Enum):
    Ordered = 0x00000001
    RetainSpecials = 0x00000002
    Raw = 0x00000004
    NoInactiveData = 0x00000008
    Readonly = 0x00000010
    ElementsAsOrdinals = 0x00000020
    Units = 0x00000040
    ElementsAsStrings = 0x00000080
    SaveRealDomain = 0x00000100
    IsLocal = 0x00000200
    CodeXmlCharacters = 0x00000400
    DoNotCheckTuples = 0x00000800
    SaveDeclDomain = 0x00001000