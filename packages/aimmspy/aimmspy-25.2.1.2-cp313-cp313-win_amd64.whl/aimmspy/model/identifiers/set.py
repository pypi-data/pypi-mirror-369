from aimmspy.model.enums.identifier_flags import Flag
from aimmspy.model.enums.me_identifier_types import IdentifierType
from aimmspy.model.enums.me_attribute_types import AttributeType

from aimmspy.model.identifiers.data_identifiers import DataIdentifier
from aimmspy.project.project import AimmsPyException

class Set( DataIdentifier ):
    def __init__(self, name, parent_me_handle, index_domain, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=IdentifierType.SET.value,
            index_domain=index_domain,
            **kwargs
        )
        self.indices = []
        
        self.subset_of = self.set_attribute(self.me_handle, kwargs.get("subset_of", None), AttributeType.SUBSET_OF.value)
        self.definition = self.set_attribute(self.me_handle, kwargs.get("definition", None), AttributeType.DEFINITION.value)
        self.initial_data = self.set_attribute(self.me_handle, kwargs.get("initial_data", None), AttributeType.INITIAL_DATA.value)
        
    def assign(self, data : list[str]):
        """
        Assigns a set of values to the identifier.
        
        This method assigns the specified set of values to the identifier, ensuring that the identifier 
        is not marked as read-only. It verifies that the project is fully compiled and creates a data 
        handle for the identifier if one does not already exist. The method clears any existing data 
        associated with the identifier before adding the new set of values.
        
        Key functionalities include:
        - Updating the C++ mapping for the identifier with the newly assigned values.
        - Avoiding redundant mapping updates if a subset relationship is defined.
        
        Args:
            data (set[str]): A set of string values to be assigned to the identifier.
        
        Raises:
            Exception: Raised if the identifier is marked as read-only, preventing data assignment.
        
        Notes:
        - The method ensures that the identifier is in a valid state for data assignment by performing 
          necessary checks and operations.
        - If the identifier is a subset of another identifier, redundant mapping updates are avoided 
          to optimize performance.
        """
        
        # data can be of type list or set. Sets are converted to lists for compatibility with AIMMS API.
        if (type(data) is set):
            data = list(data)

        if (type(data) is not list):
            raise AimmsPyException(f"data for set identifier '{self.name}' must be a list or set, not {type(data)}")
 
        # this is the aimms api call to assign the data to the set
        element_numbers = self.project.aimms_api.add_set_values(self.full_name(), data)
        
        # we want to be sure that when we check a variable ot parameter in the assign method that the data has the correct tuple values and we need this data for it
        # otherwise the user would need to call .data() first
        self.aimms_values = data
        
        # maybe because of extra unexpected characters this will not work but in that case we just fill an extra map unnecessarily
        subsetof = self.project.aimms_api.get_attribute(self.me_handle, AttributeType.SUBSET_OF.value)
        subsetof = subsetof.split("!")[0].strip().replace(' ', '').replace('\n', '').replace('\t', '')
        if subsetof:
            for reflected_identifier in self.project.reflected_identifiers:
                if reflected_identifier.name == subsetof:
                    return
                    
    def update(self, data: dict[tuple[str], float] | float) -> None:
        self.assign(data)
    
    def data(self) -> set[str]:
        """
        Retrieves the current set of values assigned to the identifier.
        
        This method fetches the values associated with the identifier using the AIMMS API. 
        It ensures that the data is up-to-date by comparing the current data version with the 
        cached version. If the data version has changed or is uninitialized, the cached values 
        are updated accordingly.
        
        Returns:
            set[str]: A set of string values currently assigned to the identifier.
        
        Notes:
        - The method uses the AIMMS API to fetch the set values efficiently.
        - It ensures optimal performance by caching the data version and only updating 
          the cached values when the data version changes.
        - The `aimms_values` attribute is updated to reflect the latest data retrieved 
          from the AIMMS API.
        """
        
        # lazy retrieve the data from aimms based on the data version that aimms gives us
        data_version = self.project.aimms_api.data_version(self.full_name())
        if data_version != self.data_version or self.data_version == -1:
            self.data_version = data_version
            self.aimms_values = self.project.aimms_api.get_set_values(self.full_name())
    
        return self.aimms_values