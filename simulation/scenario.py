import numpy as np

from simulation import measurements, station
from data.sse_streamer import SSEStreamer
import data.importer as importer

class Scenario:
    def __init__(self, name = "New"):
        self._name = str(name)
        self._measurements = measurements.Measurements()
        self._stations = []
        self._sigma = 0.0

    def anchor_positions(self):
        return np.array([anchor.position() for anchor in self.get_anchor_list()])

    def tag_positions(self):
        return np.array([tag.position() for tag in self.get_tag_list()])

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
        # TODO implement streaming
        pass

    def stop_streaming(self):
        #TODO implement streaming
        pass

    def remove_station(self, station):
        if station in self.stations:
            self.measurements.remove_station(station)
            self.stations.remove(station)

    def import_scenario(self, scenario_name, workspace_dir='workspace', agg_method='lowest'):
        try:
            ok, msg = importer.import_scenario_data(self, scenario_name, workspace_dir=workspace_dir, agg_method=agg_method)
            if ok:
                try:
                    self.name = scenario_name
                except Exception:
                    pass
            return ok, msg
        except Exception as e:
            return False, f"Importer raised exception: {e}"

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
    def streamer(self):
        return self._streamer

    @streamer.setter
    def streamer(self, value):
        self._streamer = value