from typing import Literal

import numpy as np

from agox.analysis import SearchData
from agox.models.descriptors import DescriptorBaseClass

from .property import ListPropertyData, Property


class DescriptorProperty(Property):

    def __init__(self, descriptor: DescriptorBaseClass, **kwargs) -> None:
        """
        Parameters
        ----------
        descriptor : DescriptorBaseClass
            The descriptor to compute.
        """
        super().__init__(**kwargs)
        self.descriptor = descriptor

    def compute(self, search_data: SearchData) -> ListPropertyData:
        """ """
        restarts = search_data.get_restarts()
        descriptor_list = []

        for restart in restarts:
            features = self.descriptor.get_features(restart.candidates)
            descriptor_list.append(features)

        axis_name, indices = self.get_time_axis(search_data)

        identifiers = search_data.get_all_identifiers()

        return ListPropertyData(
            name=f"Descriptor-{self.descriptor.name}",
            data=descriptor_list,
            shape=("Restarts", axis_name),
            list_axis=(identifiers, indices),
        )
