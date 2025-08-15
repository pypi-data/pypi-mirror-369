
from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType

from aimmspy.model.identifiers.data_identifiers import DataIdentifier

class Variable(DataIdentifier):
    def __init__(self, parent_me_handle, name, index_domain, **kwargs):
        
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.VARIABLE_NUMERIC.value,
            index_domain=index_domain,
            **kwargs
        )
    
        self.range = self.set_attribute(self.me_handle, kwargs.get("range", None), AttributeType.RANGE.value)
        self.definition = self.set_attribute(self.me_handle, kwargs.get("definition", None), AttributeType.DEFINITION.value)
        
    def __str__(self):
        return self.name