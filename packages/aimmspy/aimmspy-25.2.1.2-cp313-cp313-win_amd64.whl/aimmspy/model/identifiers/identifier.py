from aimmspy.model.enums.me_attribute_types import AttributeType

class Identifier:
    def __init__(self, name, parent_me_handle, identifier_type, **kwargs):
        self.name = name
        self.parent_me_handle = parent_me_handle
        self.project = kwargs.get("project", None)
        self.prefix = kwargs.get("prefix", None)
        self.comment : str = ""
        
        self.me_handle : int = kwargs.get("model_reflection_handle")
        self.comment = self.project.aimms_api.get_attribute(self.me_handle, AttributeType.COMMENT.value)
        self.comment.strip()
    
    def set_attribute(self, handle, attribute, attribute_type):
        if attribute is not None:
            self.project.aimms_api.add_attribute(handle, str(attribute), attribute_type)
        return str(attribute)
    
    def full_name(self):
        return self.prefix + "::" + self.name if self.prefix is not None else self.name

    def __str__(self) -> str:
        return self.full_name()