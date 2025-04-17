import numpy as np

from simulation import measurements, station, geometry

class Scenario:
    def __init__(self):
        self.measurements = measurements.Measurements()
        self.anchors = [
            station.Anchor([0.0, 0.0], 'Anchor A'),
            station.Anchor([10.0, 0.0], 'Anchor B'),
            station.Anchor([5.0, 8.66], 'Anchor C'),
        ]
        self.tag_truth = station.Anchor([5.0, 4.0], scenario=self)
        self.tag_estimate = station.Tag(self, 'Tag')
        self.sigma = 0.0

        self.generate_measurements(self.tag_estimate, self.tag_truth)

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.anchors])

    def generate_measurements(self, tag, model_anchor):
        for anchor in self.anchors:
            distance = np.random.normal(anchor.distance_to(model_anchor) + self.sigma, self.sigma)
            self.measurements.update_relation(frozenset([anchor, tag]), distance)
