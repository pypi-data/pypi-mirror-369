from aimmspy.model.enums.identifier_flags import Flag
from aimmspy.model.enums.me_attribute_types import AttributeType
from aimmspy.model.identifiers.identifier import Identifier
from aimmspy.utils import get_flags_from_int
from aimmspy.model.enums.data_return_types import DataReturnTypes

import pandas as pd 
import polars as pl

from datetime import datetime

import pyarrow
import sys
for path in pyarrow.get_library_dirs():
    if path not in sys.path:
        sys.path.append(path)

import aimmspy_cpp as aap

class DataIdentifier(Identifier):

    def __init__(self, name, parent_me_handle, identifier_type, index_domain, **kwargs):
        super().__init__(
            name=name,
            parent_me_handle=parent_me_handle,
            identifier_type=identifier_type,
            **kwargs
        )
        self.index_domain = []
        self.index_domain_attr = ""
        self.flags = []
        self.data_version : int = -1
        self.aimms_values = None
        
        for index in index_domain:
            self.index_domain.append(index)
        self.column_mapping = []
        
        self.me_handle = kwargs.get("model_reflection_handle") # type: ignore
        self.index_domain_attr = self.project.aimms_api.get_attribute(self.me_handle, AttributeType.INDEX_DOMAIN.value)
        self.unit_attr = self.project.aimms_api.get_attribute(self.me_handle, AttributeType.UNIT.value)
        self.flags = []
    
    def assign( self, data : dict[tuple[str], float] | pl.DataFrame | pd.DataFrame | float | str | datetime, options : dict[str, bool] = None) -> None:
        """
        Assigns data to the identifier, clearing all existing data and assigning the new data.
        
        This method assigns data to the identifier, ensuring that the identifier is not marked as read-only.
        It supports assigning data in various formats, including dictionaries for indexed values, scalar values, 
        and DataFrames. The `update` flag determines whether the existing data is cleared or updated.

        Args:
            data (dict[tuple[str], float] | pl.DataFrame | pd.DataFrame | float): The data to assign to the identifier.
                - If `data` is a dictionary, it represents indexed values, where the keys are tuples of 
                  strings corresponding to the index domain, and the values are floats.
                - If `data` is a float or int, it represents a scalar value.
                - If `data` is a pandas or polars DataFrame, it represents tabular data.
            update (bool, optional): If `True`, updates the existing data without clearing it. Defaults to `False`.
        
        Raises:
            Exception: Raised if the identifier is marked as read-only, preventing data assignment.
            Exception: Raised if the data format is not supported.
        
        Notes:
        - For dictionaries, the keys are transformed into element tuples based on the index domain before 
          assigning the data.
        - For scalar values, the data is directly assigned without indexing.
        - For DataFrames, the data is converted to an appropriate format (e.g., Arrow) before assignment.
        - The method ensures that the identifier is in a valid state for data assignment by performing 
          necessary checks and operations.
        """
        if options is None:
            options = {}

        if ('update' not in options):
            options["update"] = False

        self.flags = get_flags_from_int(self.project.find_identifier_info(self.full_name(), True).flags, Flag)
        
        if Flag.Readonly in self.flags:
            raise Exception(f"The identifier '{self.full_name()}' is marked as read-only and cannot be assigned data.")
        
        if isinstance(data, dict):
            
            # check that data and options are not swapped can only contain keys update, extendType, mapping
            for key in options.keys():
                if key not in ["update", "extendType", "mapping"]:
                    raise Exception(f"The option '{key}' is not a valid option valid options are 'update', 'extendType', 'mapping' did you swap data and options?")
            
            self.project.aimms_api.add_values(self.full_name(), data, options)
            return
        
        
        # this case is it for scalar values which means values without an index single values
        elif isinstance(data, float) or isinstance(data, int) or isinstance(data, str) or isinstance(data, datetime):
            self.project.aimms_api.add_value(self.full_name(), aap.int_vector(), data, options)
            return

        elif isinstance(data, pd.DataFrame):
            self.project.aimms_api.add_values_dataframe_arrow(self.full_name(), pyarrow.Table.from_pandas(data), options)
            return
        
        elif isinstance(data, pl.DataFrame):
            self.project.aimms_api.add_values_dataframe_arrow(self.full_name(), data.to_arrow(), options)
            return

        raise Exception("The data you are trying to assign is not in the correct format")
        
    
    def update(self, data : dict[tuple[str | datetime], float] | pl.DataFrame | pd.DataFrame | float, options: dict[str, bool] = None) -> None:
        """
        Updates the data of the identifier without clearing the existing data.
        
        This method updates the data of the identifier, ensuring that the identifier is not marked as read-only.
        It supports updating data in various formats, including dictionaries for indexed values, scalar values, 
        and DataFrames.
        
        Args:
            data (dict[tuple[str], float] | pl.DataFrame | pd.DataFrame | float): The data to update the identifier with.
                - If `data` is a dictionary, it represents indexed values, where the keys are tuples of 
                  strings corresponding to the index domain, and the values are floats.
                - If `data` is a float or int, it represents a scalar value.
                - If `data` is a pandas or polars DataFrame, it represents tabular data.
        
        Raises:
            Exception: Raised if the identifier is marked as read-only, preventing data updates.
        
        Notes:
        - This method internally calls the `assign` method with the `update` flag set to `True`.
        - For dictionaries, the keys are transformed into element tuples based on the index domain before 
          updating the data.
        - For scalar values, the data is directly updated without indexing.
        - The method ensures that the identifier is in a valid state for data updates by performing 
          necessary checks and operations.
        """

        if options is None:
            options = {}
        options["update"] = True
        
        self.assign(data, options)
    
    def data(self, options: dict = None) -> dict[tuple[str], float] | pl.DataFrame | pd.DataFrame | float:
        """
        Retrieves the data associated with the identifier.
        
        This method fetches the data for the identifier, ensuring that all internal data structures 
        are up-to-date. It supports scalar values, indexed data, and multiple data return types.
        
        Args:
            mapping (list[str], optional): A list of mappings to filter the data retrieval. Defaults to an empty list.
        
        Returns:
            dict[tuple[str], float] | pl.DataFrame | pd.DataFrame | float: 
                - If the identifier has an index domain and the preferred return type is `DICT`, a dictionary is returned 
                  where the keys are tuples of strings representing the index domain, and the values are floats.
                - If the preferred return type is `PANDAS`, a pandas DataFrame is returned.
                - If the preferred return type is `POLARS`, a polars DataFrame is returned.
                - If the preferred return type is `ARROW`, a pyarrow Table is returned.
                - If the identifier is scalar, a single float value is returned.
        
        Notes:
        - For variables, ensure that a procedure has been executed before calling this method 
          to guarantee that the data is available.
        - The method updates the internal data version and caches the retrieved values to 
          optimize performance.
        - Scalar and indexed data are handled differently to ensure efficient retrieval.
        - The preferred data return type is determined by the `data_type_preference` attribute of the project.
        """

        if options is None:
            options = {}

        data_version : int = self.project.aimms_api.data_version(self.full_name())
        mapping : list[str] = options.get("mapping", [])

        data_type_preference = options.get("return_type", self.project.data_type_preference)
        
        if data_version != self.data_version or self.data_version == -1 or self.column_mapping != mapping or self.data_type_preference != data_type_preference:
            self.data_version = data_version
            self.column_mapping = mapping
            self.data_type_preference = data_type_preference
        
            # for scalar values we just get the value this is a different api call so we need to handle it differently
            dimension : int = self.project.aimms_api.get_identifier_cardinality(self.project.find_identifier_info(self.full_name(), True).data_handle)
            if dimension == 0:
                self.aimms_values : float = self.project.aimms_api.get_value(self.full_name(), aap.int_vector())
            
            # for indexed values we get the values we want to do it efficiently so we get all the values at once
            else:
                if data_type_preference == DataReturnTypes.ARROW:
                    self.aimms_values : pyarrow.Table = self.project.aimms_api.get_values_dataframe_arrow(self.full_name(), mapping)
                elif data_type_preference == DataReturnTypes.PANDAS:
                    arrow_table = self.project.aimms_api.get_values_dataframe_arrow(self.full_name(), mapping)
                    if arrow_table:
                        self.aimms_values : pd.DataFrame = arrow_table.to_pandas()
                    
                elif data_type_preference == DataReturnTypes.POLARS:
                    arrow_table = self.project.aimms_api.get_values_dataframe_arrow(self.full_name(), mapping)
                    if arrow_table:
                        self.aimms_values : pl.DataFrame = pl.from_arrow(arrow_table)
                        
                elif data_type_preference == DataReturnTypes.DICT:
                    self.aimms_values : dict[tuple[str | datetime], float | str] = self.project.aimms_api.get_values(self.full_name())
                else:
                    raise Exception("The type you are trying to get is not supported")
        return self.aimms_values