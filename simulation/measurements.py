
class Measurements:
    def __init__(self) -> None:
        self.relation = {}

    def find_relation(self, single_or_pair):
        return [(pair, distance) for pair, distance in self.relation.items() if single_or_pair in pair]

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