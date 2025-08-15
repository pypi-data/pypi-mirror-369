
from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType

from aimmspy.model.identifiers.data_identifiers import DataIdentifier
        
class Parameter(DataIdentifier):
    def __init__(self, parent_me_handle, name, index_domain, identifier_type, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=identifier_type,
            index_domain=index_domain,
            **kwargs
        )
        
        self.definition = self.set_attribute(self.me_handle, kwargs.get("definition", None), AttributeType.DEFINITION.value)
        self.initial_data = self.set_attribute(self.me_handle, kwargs.get("initial_data", None), AttributeType.INITIAL_DATA.value)

class NumericParameter(Parameter):
    def __init__(self, parent_me_handle, name, index_domain, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.PARAMETER_NUMERIC.value,
            index_domain=index_domain,
            **kwargs
        )

class StringParameter(Parameter):
    def __init__(self, parent_me_handle, name, index_domain, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.PARAMETER_STRING.value,
            index_domain=index_domain,
            **kwargs
        )

class ElementParameter(Parameter):
    def __init__(self, parent_me_handle, name, index_domain, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.PARAMETER_ELEMENT.value,
            index_domain=index_domain,
            **kwargs
        )        