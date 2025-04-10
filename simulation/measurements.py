import station as st

class Measurements:
    def __init__(self) -> None:
        self.relation = set()

    def find_relation(self, single_or_pair):
        return [(pair_in_rel, distance) for pair_in_rel, distance in self.relation if single_or_pair in pair_in_rel]

    def update_relation(self, pair, distance: float):

        if not isinstance(pair, frozenset):
            raise ValueError("Pair must be a frozen set")
        if len(pair) != 2:
            raise ValueError("Pair must have two elements")

        for pair_in_rel, distance_in_rel in self.relation:
            if pair == pair_in_rel:
                self.relation.remove((pair, distance_in_rel))
                self.relation.add((pair, distance))
                return

        self.relation.add((pair, distance))

    def remove_station(self, station: st.Station):
        for pair, distance in self.relation:
            if station in pair:
                self.relation.remove((pair, distance))