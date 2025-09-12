import numpy as np

from simulation import measurements, station
from data.sse_streamer import SSEStreamer
import data.importer as importer

class Scenario:
    def __init__(self):
        self.measurements = measurements.Measurements()
        self.stations = [
            station.Anchor([0.5, 0.5], 'Anchor A'),
            station.Anchor([10.0, 0.0], 'Anchor B'),
            station.Anchor([5.0, 8.66], 'Anchor C'),
            station.Tag(self, '⍺'),
            station.Tag(self, 'β'),
            #station.Tag(self, 'SANDBOX_TAG')
        ]
        self.tag_truth = station.Anchor([5.0, 4.0], scenario=self)
        self.sigma = 0.0

        self.streamer = None

        # Generate measurements for all tags
        for tag in self.get_tag_list():
            self.generate_measurements(tag, self.tag_truth)

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.get_anchor_list()])

    def tag_positions(self):
        return np.array([tag.position() for tag in self.get_tag_list()])

    def generate_measurements(self, tag_estimate, tag_truth):
        for anchor in self.get_anchor_list():
            distance = np.random.normal(anchor.distance_to(tag_truth) + self.sigma, self.sigma)
            # Removed clear_unused to preserve all measurements
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
        return [s for s in self.stations if isinstance(s, station.Anchor)]

    def start_streaming(self, url):
        self.streamer = SSEStreamer(url, self)

    def stop_streaming(self):
        if self.streamer:
            # SSEStreamer exposes stop_streaming(); keep same call to remain compatible
            try:
                self.streamer.stop_streaming()
            except Exception:
                pass
            self.streamer = None

    def remove_station(self, station):
        if station in self.stations:
            self.measurements.remove_station(station)
            self.stations.remove(station)

    def import_scenario(self, scenario_name, workspace_dir='workspace', agg_method='lowest'):
        """
        Trigger importing CSV scenario data into this Scenario instance.

        Returns:
            (success: bool, message: str)
        """
        try:
            ok, msg = importer.import_scenario_data(self, scenario_name, workspace_dir=workspace_dir, agg_method=agg_method)
            return ok, msg
        except Exception as e:
            return False, f"Importer raised exception: {e}"