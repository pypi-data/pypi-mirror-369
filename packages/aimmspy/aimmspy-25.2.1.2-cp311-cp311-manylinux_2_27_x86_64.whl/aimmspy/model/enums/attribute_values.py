from enum import Enum

class Attribute():
    class Direction(Enum):
        MINIMIZE = "minimize"
        MAXIMIZE = "maximize"
        
        def __str__(self):
            return self.value
    
    class Range(Enum):
        NONNEGATIVE = "Nonnegative"
        NONPOSITIVE = "Nonpositive"
        REAL = "Real"
        INTEGER = "Integer"
        BINARY = "Binary"

        def __str__(self):
            return self.value