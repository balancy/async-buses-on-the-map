from dataclasses import dataclass


@dataclass
class Bus:
    busId: str
    route: str
    lat: str = None
    lng: str = None

    def update_coordinates(self, lat, lng):
        self.lat = lat
        self.lng = lng


@dataclass
class WindowBounds:
    south_lat: str = None
    north_lat: str = None
    west_lng: str = None
    east_lng: str = None

    def update(self, south_lat, north_lat, west_lng, east_lng):
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng

    def are_set(self):
        return self.south_lat
