
class Measurements:
    def __init__(self) -> None:
        self.relation = {}

    def find_relation_pair_distance(self, station_pair):
        if not isinstance(station_pair, frozenset):
            raise ValueError("Pair must be a frozenset")
        if len(station_pair) != 2:
            raise ValueError("Pair must have two elements")

        result = self.relation.get(station_pair, None)
        return result

    def find_relation_single(self, station_single):
        return [(pair, distance) for pair, distance in self.relation.items() if station_single in pair]

    def update_relation(self, pair, distance: float):
        if not isinstance(pair, frozenset):
            raise ValueError("Pair must be a frozenset")
        if len(pair) != 2:
            raise ValueError("Pair must have two elements")

        self.relation[pair] = distance

    def clear_unused(self, used_stations):
        self.relation = {pair: distance for pair, distance in self.relation.items() if all(station in used_stations for station in pair)}

    def remove_station(self, station):
        self.relation = {pair: distance for pair, distance in self.relation.items() if station not in pair}

    def __str__(self):
        return f"Measurements(relation={self.relation})"

    def __repr__(self):
        return f"Measurements(relation={self.relation})"