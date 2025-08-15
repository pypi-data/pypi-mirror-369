

from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType
from aimmspy.model.identifiers.identifier import Identifier
     
class Procedure(Identifier):
    def __init__(self, name, parent_me_handle, **kwargs):
        
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.PROCEDURE.value,
            **kwargs
        )
    
    def __call__(self, **kwargs):
        return self.project.aimms_api.run_procedure(self.full_name(), **kwargs)