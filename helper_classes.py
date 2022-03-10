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
            raise WindowBoundsException(
                {
                    'msgType': 'JSONDecodeError',
                    'errors': [exc.args],
                }
            )
        except pydantic.ValidationError as exc:
            raise WindowBoundsException(
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
            raise IncorrectBusException(
                {
                    'msgType': 'JSONDecodeError',
                    'errors': [exc.args],
                }
            )
        except pydantic.ValidationError as exc:
            raise IncorrectBusException(
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


class WindowBoundsException(Exception):
    pass


class IncorrectBusException(Exception):
    pass


if __name__ == '__main__':
    message = 'salut'
    message = (
        '{"data":{"south_lat":55.727011350768876,'
        '"north_lat":55.78878211812553,"west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}'
    )

    bounds = WindowBounds()
    try:
        bounds.update_from_message(message)
    except WindowBoundsException as exc:
        exc_message, *_ = exc.args
        print(exc_message)
