from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.identifiers.identifier import Identifier

class DeclarationSection(Identifier):
    def __init__(self, name, parent_me_handle, **kwargs):
        
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.DECLARATION_SECTION.value,
            **kwargs
        )
