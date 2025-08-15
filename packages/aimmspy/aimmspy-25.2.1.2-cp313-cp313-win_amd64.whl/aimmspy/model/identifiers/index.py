
from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType
from aimmspy.model.identifiers.identifier import Identifier

class Index(Identifier):
    def __init__(self, parent_me_handle, name, range= None, **kwargs):
        
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.INDEX.value,
            **kwargs
        )
        
        self.range = None
        self.me_handle = kwargs.get("model_reflection_handle") # type: ignore

    def __str__(self):
        return self.name