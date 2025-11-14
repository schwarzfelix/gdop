from abc import ABC, abstractmethod
import numpy as np

from simulation import geometry

def distance_between(station1, station2, measurements=None):
    if measurements is None:
        if isinstance(station1, Tag) and station1.scenario is not None:
            measurements = station1.scenario.measurements
        elif isinstance(station2, Tag) and station2.scenario is not None:
            measurements = station2.scenario.measurements

    if measurements is not None:
        measured_distance = measurements.find_relation_pair_distance(frozenset({station1, station2}))
        if measured_distance is not None:
            return measured_distance

    calculated_distance = geometry.distance_between(station1.position(), station2.position())
    return calculated_distance

class Station(ABC):
    def __init__(self, scenario=None, name=None):
        self._scenario = scenario
        self._name = name

    @property
    def scenario(self):
        return self._scenario

    @abstractmethod
    def position(self):
        pass

    @abstractmethod
    def distance_to(self, other):
        pass

    @abstractmethod
    def distances(self):
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

class Anchor(Station):

    def __init__(self, position, name='FixedDevice', scenario=None):
        super().__init__(scenario, name)
        self._position = np.array(position)

    def position(self, exclude=None):
        return self._position.copy()

    def update_position(self, position):
        self._position = np.array(position)

    def distance_to(self, other: Station):
        return distance_between(self, other)

    def distances(self, scenario=None):
        if scenario is None:
            scenario = self.scenario
        if scenario is None:
            raise ValueError("Scenario must be provided to calculate distances.")
        if len(scenario.anchor_positions()) < 1:
            return np.array([])

        return geometry.euclidean_distances(scenario.anchor_positions(), self.position())

class Tag(Station):

    def __init__(self, scenario, name='LocalizedDevice'):
        super().__init__(scenario, name)

    def position(self, exclude=None, trilateration_method=None):

        if exclude is None:
            exclude = {self}
        exclude |= {self}
        relation_subset = self.scenario.measurements.find_relation_single(self)

        anchor_count = 0
        for measurement in relation_subset:
            partner = next(iter(measurement[0].copy() - {self}))
            if partner in exclude or not isinstance(partner, Anchor):
                continue
            anchor_count += 1

        if anchor_count < 1:
            return [0, 0]

        station_positions = []
        distances = []

        for measurement in relation_subset:
            partner = next(iter(measurement[0].copy() - {self}))
            if partner in exclude:
                continue
            station_positions.append(partner.position(exclude))
            distances = np.append(distances, measurement[1])

        # Use method from scenario if not explicitly provided
        if trilateration_method is None:
            trilateration_method = getattr(self.scenario, 'trilateration_method', 'classical')

        # Use robust trilateration if requested
        if trilateration_method in ["best_subset", "nonlinear"]:
            position, metadata = geometry.trilateration_robust(
                np.array(station_positions), 
                np.array(distances),
                method=trilateration_method
            )
            # Store metadata for debugging/analysis (optional)
            if hasattr(self, '_trilateration_metadata'):
                self._trilateration_metadata = metadata
            return position
        else:
            # Classical method
            return geometry.trilateration(np.array(station_positions), np.array(distances))

    def distance_to(self, other: Station):
        return distance_between(self, other, self.scenario.measurements)

    def distances(self):
        anchors = self.scenario.anchor_positions()
        if anchors is None or anchors.size == 0:
            return np.array([])
        return geometry.euclidean_distances(anchors, self.position())

    def dilution_of_precision(self):
        return geometry.dilution_of_precision(self.scenario.anchor_positions(), self.position(), self.distances())

    def position_error(self):
        if self.scenario and self.scenario.tag_truth:
            return geometry.distance_between(self.position(), self.scenario.tag_truth.position())
        return None