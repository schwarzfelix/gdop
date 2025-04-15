import numpy as np
from typing import cast

from simulation import measurements, station, geometry

class Scenario:
    def __init__(self):
        self.measurements = measurements.Measurements()
        self.anchors = [
            station.Anchor([0.0, 0.0], 'Anchor A'),
            station.Anchor([10.0, 0.0], 'Anchor B'),
            station.Anchor([5.0, 8.66], 'Anchor C'),
        ]
        self.tag_truth = station.Anchor([5.0, 4.0])
        self.tag_estimate = station.Tag(self, 'Tag')
        self.sigma = 0.0

        self.update_measurements()

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.anchors])

    def dilution_of_precision(self):
        return geometry.dilution_of_precision(self.anchor_positions(), self.tag_estimate.position(), self.tag_estimate.distances())

    def update_measurements(self):
        for anchor in self.anchors:
            self.measurements.update_relation(frozenset([anchor, self.tag_estimate]), anchor.distance_to(self.tag_truth))
