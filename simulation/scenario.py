import numpy as np

from simulation import measurements, station, geometry

class Scenario:
    def __init__(self, name = "New"):
        self._name = str(name)
        self._measurements = measurements.Measurements()
        self._stations = []
        self._sigma = 0.0
        self._tag_truth = station.Anchor([0.0, 0.0], 'TAG_TRUTH')
        self._border_rectangle = None

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.get_anchor_list()])

    def tag_positions(self):
        return np.array([tag.position() for tag in self.get_tag_list()])

    def get_station_by_name(self, name):
        for s in self.stations:
            if str(s.name) == str(name):
                return s
        new_station = station.Tag(self, name)
        self.stations.append(new_station)
        return new_station

    def get_tag_list(self):
        return [s for s in self.stations if isinstance(s, station.Tag)]

    def get_anchor_list(self):
        return [s for s in self.stations if isinstance(s, station.Anchor)]

    def remove_station(self, station):
        if station in self.stations:
            self.measurements.remove_station(station)
            self.stations.remove(station)

    def get_gdop_for_position(self, position):
        return geometry.dilution_of_precision(self.anchor_positions(), position)

    def get_tag_truth_gdop(self):
        return self.get_gdop_for_position(self.tag_truth.position())

    def get_expected_measurements(self):
        """
        Calculate expected measurements based on Euclidean distance between tag_truth and each anchor.
        
        Returns:
            dict: Dictionary with frozenset([anchor, tag_truth]) as keys and distances as values.
        """
        expected = {}
        tag_truth_pos = self.tag_truth.position()
        for anchor in self.get_anchor_list():
            pair = frozenset([anchor, self.tag_truth])
            distance = geometry.euclidean_distance(anchor.position(), tag_truth_pos)
            expected[pair] = distance
        return expected

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def measurements(self):
        return self._measurements
    
    @measurements.setter
    def measurements(self, value):
        self._measurements = value

    @property
    def stations(self):
        return self._stations
    
    @stations.setter
    def stations(self, value):
        self._stations = list(value)

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, value):
        self._sigma = float(value)

    @property
    def tag_truth(self):
        return self._tag_truth
    
    @tag_truth.setter
    def tag_truth(self, value):
        self._tag_truth = value

    @property
    def border_rectangle(self):
        return self._border_rectangle
    
    @border_rectangle.setter
    def border_rectangle(self, value):
        self._border_rectangle = value