from abc import ABC, abstractmethod
from typing import Any, List, Literal, Tuple, Union

import numpy as np

from agox.analysis.search_data import SearchCollection, SearchData


class PropertyData(ABC):
    def __init__(self, data: Any, name: str) -> None:
        self.data = data
        self.name = name


class ArrayPropertyData(PropertyData):
    def __init__(self, data: np.ndarray, name: str, shape: Tuple[str], array_axis: Tuple[np.ndarray]) -> None:
        """
        Multidimensional array property data.

        E.g. for energy this is a 2D array with shape (Restarts, Iterations) and each entry is the energy of the configuration.

        Parameters
        ----------
        property_name : str
            Name of the property
        property_shape : Tuple[str]
            Shape of the property, e.g ('Restarts', 'Iterations') for a 2D array
        """
        super().__init__(data=data, name=name)
        self.shape = shape
        self.axis = array_axis


class ListPropertyData(PropertyData):
    def __init__(self, data: List[Any], name: str, shape: Tuple[str], list_axis: Tuple[Any]) -> None:
        """
        Parameters
        ----------
        property_name : str
            Name of the property
        """
        super().__init__(data=data, name=name)
        self.shape = shape
        self.axis = list_axis

    def __repr__(self) -> str:
        return f"{self.name}:\n{self.shape}"


class Property(ABC):

    def __init__(self, 
                time_axis: np.ndarray = None, 
                time_unit: Literal["s", "m", "h", "d", "y"] = "s", 
                cost_factor: int = 1) -> None:
        """
        Get the energy of the system as a np.array of shape [restarts, iterations].
        """
        if time_axis is None:
            time_axis = "indices"

        if time_axis not in ["indices", "iterations", "time"]:
            raise ValueError("time_axis must be one of ['indices', 'iterations', 'time']")

        self.time_axis = time_axis
        self.time_unit_symbol = time_unit
        
        if time_unit == "s":
            self.unit = 1
        elif time_unit == "m":
            self.unit = 60
        elif time_unit == "h":
            self.unit = 3600
        elif time_unit == "d":
            self.unit = 86400        
        elif time_unit == "y":
            self.unit = 31536000
        else:
            raise ValueError("time_unit must be one of ['s', 'm', 'h', 'd']")
        
        self.cost_factor = cost_factor

    def get_time_axis(self, search_data: SearchData) -> str:
        axis_name = self.time_axis.capitalize()

        if self.time_axis == "indices":
            indices = search_data.get_all("indices", fill=np.nan)
        elif self.time_axis == "iterations":
            indices = search_data.get_all("iterations", fill=np.nan)
        else:
            indices = search_data.get_all("times", fill=np.nan) / self.unit * self.cost_factor
            if self.cost_factor == 1:
                axis_name = axis_name + f" [{self.time_unit_symbol}]"
            else:
                axis_name = f"CPU cost [{self.time_unit_symbol}]"

        if self.time_axis in ["indices", "iterations"]:
            axis_name = f"{axis_name} [#]"

        return axis_name, indices

    @abstractmethod
    def compute(self, search_data: SearchData) -> PropertyData:
        pass

    def __call__(self, search_data: SearchData) -> PropertyData:
        return self.compute(search_data)

    def get_minimum(self, searches: Union[SearchCollection, List[SearchData]]) -> float:
        min_value = np.inf
        for search in searches:
            prop = self(search)
            if isinstance(prop, ArrayPropertyData):
                min_value = min(min_value, np.nanmin(prop.data))
            else:
                raise ValueError(f"Property {prop} is not an ArrayPropertyData")

        return min_value
