
from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType
from aimmspy.model.identifiers.identifier import Identifier

class MathematicalProgram(Identifier):
    def __init__(self, name, parent_me_handle, **kwargs):
        
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.MATHEMATICAL_PROGRAM.value,
            **kwargs
        )
        
        self.direction = self.set_attribute(self.me_handle, kwargs.get("direction", "minimize"), AttributeType.DIRECTION.value)
        self.objective = self.set_attribute(self.me_handle, kwargs.get("objective", None), AttributeType.OBJECTIVE.value)
        self.type = self.set_attribute(self.me_handle, kwargs.get("type", "automatic"), AttributeType.TYPE.value)
