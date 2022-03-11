import json
from dataclasses import dataclass

import pydantic


@dataclass
class Bus:
    busId: str
    route: str
    lat: float = 0
    lng: float = 0

    def update_coordinates(self, lat, lng):
        self.lat = lat
        self.lng = lng

    @classmethod
    def create_from(cls, message):
        try:
            decoded_message = json.loads(message)
            BusSchema.parse_obj(decoded_message)
        except json.JSONDecodeError as exc:
            raise InvalidDataFormatException(
                {
                    'msgType': 'JSONDecodeError',
                    'errors': [exc.args],
                }
            )
        except pydantic.ValidationError as exc:
            raise InvalidDataFormatException(
                {
                    'msgType': 'ValidationError',
                    'errors': [error for error in exc.errors()],
                }
            )
        else:
            return cls(**decoded_message)


@dataclass
class WindowBounds:
    south_lat: float = 0
    north_lat: float = 0
    west_lng: float = 0
    east_lng: float = 0

    def __update(self, south_lat, north_lat, west_lng, east_lng):
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng

    def update_from_message(self, message):
        try:
            decoded_message = json.loads(message)
            WindowBoundsMessageSchema.parse_obj(decoded_message)
        except json.JSONDecodeError as exc:
            raise InvalidDataFormatException(
                {
                    'msgType': 'JSONDecodeError',
                    'errors': [exc.args],
                }
            )
        except pydantic.ValidationError as exc:
            raise InvalidDataFormatException(
                {
                    'msgType': 'ValidationError',
                    'errors': [error for error in exc.errors()],
                }
            )
        else:
            self.__update(**decoded_message['data'])

    def are_set(self):
        return self.south_lat


class BusSchema(pydantic.BaseModel):
    busId: str
    route: str
    lat: float
    lng: float


class WindowBoundsSchema(pydantic.BaseModel):
    south_lat: float
    north_lat: float
    west_lng: float
    east_lng: float


class WindowBoundsMessageSchema(pydantic.BaseModel):
    msgType: str
    data: WindowBoundsSchema


class InvalidDataFormatException(Exception):
    pass
