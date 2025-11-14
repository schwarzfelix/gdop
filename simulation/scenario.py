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
        self._trilateration_method = "classical"  # Default method
        self._raw_measurement_counts = {}  # Dict mapping anchor name -> count of raw measurements

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

    def get_measurement_errors(self):
        """
        Calculate measurement errors by comparing actual measurements to expected distances.
        
        Returns:
            dict: Dictionary with frozenset([anchor, tag]) as keys and error values as values.
                  Error is calculated as: measured_distance - expected_distance
        """
        errors = {}
        expected = self.get_expected_measurements()
        
        for pair, measured_distance in self.measurements.relation.items():
            # Find corresponding expected measurement
            # The pair in measurements might be [anchor, tag], we need to match it with [anchor, tag_truth]
            station1, station2 = pair
            
            # Check if one of the stations is a Tag (localized device)
            from simulation.station import Tag
            tag = None
            anchor = None
            
            if isinstance(station1, Tag):
                tag = station1
                anchor = station2
            elif isinstance(station2, Tag):
                tag = station2
                anchor = station1
            
            if tag is not None and anchor is not None:
                # Find the expected measurement for this anchor
                expected_pair = frozenset([anchor, self.tag_truth])
                if expected_pair in expected:
                    expected_distance = expected[expected_pair]
                    error = measured_distance - expected_distance
                    errors[pair] = error
        
        return errors

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

    @property
    def trilateration_method(self):
        return self._trilateration_method
    
    @trilateration_method.setter
    def trilateration_method(self, value):
        """Set trilateration method: 'classical', 'best_subset', or 'nonlinear'"""
        if value not in ["classical", "best_subset", "nonlinear"]:
            raise ValueError(f"Invalid trilateration method: {value}")
        self._trilateration_method = value

    @property
    def raw_measurement_counts(self):
        """Get dictionary of raw measurement counts per anchor before aggregation."""
        return self._raw_measurement_counts
    
    @raw_measurement_counts.setter
    def raw_measurement_counts(self, value):
        """Set dictionary of raw measurement counts per anchor before aggregation."""
        self._raw_measurement_counts = dict(value) if value else {}
