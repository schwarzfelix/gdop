import numpy as np

from .scenario import Scenario
from simulation import measurements, station
from data.sse_streamer import SSEStreamer


class SandboxScenario(Scenario):

    def __init__(self, name="Sandbox"):
        super().__init__(name)

        self.stations = [
            station.Anchor([0.5, 0.5], 'Anchor A'),
            station.Anchor([10.0, 0.0], 'Anchor B'),
            station.Anchor([5.0, 8.66], 'Anchor C'),
            #station.Anchor([5.0, 4.0], 'TAG_TRUTH'),
            station.Tag(self, 'SANDBOX_TAG')
        ]
        
        self.tag_truth = station.Anchor([5.0, 4.0], 'TAG_TRUTH')

        for tag in self.get_tag_list():
            self.generate_measurements(tag, self.tag_truth)

    def generate_measurements(self, tag_estimate, tag_truth):
        for anchor in self.get_anchor_list():
            # TODO this ignores the TAG_TRUTH as an Anchor. Make sure it is never used for positioning or GDOP calculation
            if np.array_equal(anchor.position(), tag_truth.position()):
                continue
            distance = np.random.normal(anchor.distance_to(tag_truth) + self.sigma, self.sigma)
            self.measurements.update_relation(frozenset([anchor, tag_estimate]), distance)

