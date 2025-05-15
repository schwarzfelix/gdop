import numpy as np

from simulation import measurements, station, geometry

class Scenario:
    def __init__(self):
        self.measurements = measurements.Measurements()
        self.stations = [
            station.Anchor([0.0, 0.0], 'Anchor A'),
            station.Anchor([10.0, 0.0], 'Anchor B'),
            station.Anchor([5.0, 8.66], 'Anchor C'),
        ]
        self.tag_truth = station.Anchor([5.0, 4.0], scenario=self)
        self.tag_estimate = station.Tag(self, 'Tag')
        self.sigma = 0.0

        self.generate_measurements(self.tag_estimate, self.tag_truth)

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.get_anchor_list()])

    def generate_measurements(self, tag_estimate, tag_truth):
        for anchor in self.get_anchor_list():
            distance = np.random.normal(anchor.distance_to(tag_truth) + self.sigma, self.sigma)
            self.measurements.clear_unused(self.get_anchor_list() + [tag_estimate])
            self.measurements.update_relation(frozenset([anchor, tag_estimate]), distance)

    def get_station_by_name(self, name):
        for s in self.stations:
            if str(s.name()) == str(name):
                return s
        new_station = station.Tag(self, name)
        self.stations.append(new_station)
        return new_station

    def get_tag_list(self):
        return [s for s in self.stations if isinstance(s, station.Tag)]

    def get_anchor_list(self):
        #return self.anchors
        return [s for s in self.stations if isinstance(s, station.Anchor)]