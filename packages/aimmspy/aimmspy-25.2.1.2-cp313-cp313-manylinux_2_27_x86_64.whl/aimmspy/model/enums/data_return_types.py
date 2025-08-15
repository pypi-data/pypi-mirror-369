from enum import Enum 

class DataReturnTypes(Enum):
    """
    Enum to specify the return type of the data method.
    
    Attributes:
        dict: Represents a dictionary return type.
        arrow: Represents an Arrow table return type.
    """
    DICT = 0
    ARROW = 1
    PANDAS = 2
    POLARS = 3
