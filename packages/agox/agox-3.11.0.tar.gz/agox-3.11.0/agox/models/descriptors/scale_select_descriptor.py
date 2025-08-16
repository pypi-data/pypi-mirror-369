import numpy as np
from sklearn.preprocessing import StandardScaler

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.observer import Observer
from agox.writer import Writer


class ScaleSelectDescriptor(DescriptorBaseClass, Observer):
    name = "ScaleSelectDescriptor"
    descriptor_type = "local"
    dynamic_attributes = ["scaler", "selected_features"]

    def __init__(
        self,
        base_descriptor,
        database=None,
        transfer_data=None,
        iteration_to_update=10,
        variance_threshold=0.1,
        scale=True,
        order=0,
        **kwargs,
    ):
        DescriptorBaseClass.__init__(self, environment=base_descriptor.environment, use_cache=False, **kwargs)
        Observer.__init__(self, order=order)

        self.base_descriptor = base_descriptor
        self.descriptor_type = base_descriptor.descriptor_type
        self.variance_threshold = variance_threshold
        self.transfer_data = transfer_data if transfer_data is not None else []
        self.iteration_to_update = iteration_to_update
        self.scale = scale

        # Initialize for Ray.
        self.scaler = None
        self.selected_features = None

        if database is not None:
            self.add_observer_method(self.update_observer, sets=self.sets[0], gets=self.gets[0], order=self.order[0])
            self.attach(database)

    def update(self, dataset):
        self.scaler = StandardScaler()
        X = np.vstack([self.base_descriptor.get_features(atoms).reshape(len(atoms), -1) for atoms in dataset])
        self.scaler.fit(X)
        self.selected_features = self.scaler.scale_ > self.variance_threshold
        self.writer("Selected {} out of {} features".format(self.selected_features.sum(), len(self.selected_features)))

    def create_features(self, dataset):
        X = self.base_descriptor.get_features(dataset)
        if self.scaler is not None:
            if self.scale:
                X = self.scaler.transform(X)
            X = X[:, self.selected_features]
        return X

    def create_feature_gradient(self, dataset):
        X = self.base_descriptor.get_feature_gradient(dataset)
        if self.scaler is not None:
            if self.scale:
                X = X / self.scaler.scale_[None, None, None, :]
            X = X[:, :, :, self.selected_features]
        return X

    def get_number_of_centers(self, atoms):
        return self.base_descriptor.get_number_of_centers(atoms)

    @Observer.observer_method
    def update_observer(self, database, state):
        iteration = self.get_iteration_counter()
        if iteration >= self.iteration_to_update:
            data = database.get_all_candidates()
            all_data = data + self.transfer_data
            self.update(all_data)

    def __hash__(self):
        return 123456789  # EXTREMELY HACKY VERY DANGER?
