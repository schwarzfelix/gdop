from abc import ABC, abstractmethod
import numpy as np

from simulation import geometry

def distance_between(station1, station2, measurements=None):
    if measurements is None and isinstance(station1, Tag):
        measurements = station1.measurements
    if measurements is None and isinstance(station2, Tag):
        measurements = station2.measurements

    if measurements is not None:
        pair, measured_distance = measurements.find_relation({station1, station2})
        if measured_distance is not None:
            return measured_distance

    calculated_distance = geometry.distance_between(station1.position(), station2.position())
    return calculated_distance

class Station(ABC):

    @abstractmethod
    def position(self):
        pass

    @abstractmethod
    def distance_to(self, other):
        pass

    @abstractmethod
    def name(self):
        pass

    def __str__(self):
        return self.name()

class Anchor(Station):

    def __init__(self, position, name='FixedDevice'):
        self._position = np.array(position)
        self._name = name

    def position(self, exclude=None):
        return self._position

    def distance_to(self, other: Station):
        return distance_between(self, other)

    def name(self):
        return self._name

class Tag(Station):

    def __init__(self, scenario, name='LocalizedDevice'):
        self.scenario = scenario
        self.measurements = self.scenario.measurements
        self._name = name

    def position(self, exclude=None):

        if exclude is None:
            exclude = {self}
        exclude |= {self}

        relation_subset = self.measurements.find_relation(self)

        satellite_positions = []
        distances = []

        for measurement in relation_subset:
            partner = next(iter(measurement[0].copy() - {self}))
            if partner in exclude:
                continue
            satellite_positions.append(partner.position(exclude))
            distances = np.append(distances, measurement[1])

        return geometry.trilateration(np.array(satellite_positions), np.array(distances))

    def distance_to(self, other: Station):
        return distance_between(self.measurements, self, other)

    def distances(self):
        return geometry.euclidean_distances(self.scenario.anchor_positions(), self.position())

    def name(self):
        return self._name