from event import Event
from db import cursor
from to_object import to_event

class Track:

    def __init__(self, id: int, name: str, city: str, country: str, outdoor: bool, altitude: int) -> None:
        self._id = id
        self._name = name
        self._city = city
        self._country = country
        self._outdoor = outdoor
        self._altitude = altitude

    def get_events(self) -> list[Event]:
        query = cursor.execute('''
            SELECT events.*
            FROM tracks, events
            WHERE tracks.id = ?
            AND tracks.id = events.track_id
        ''', (self._id,))
        return to_event(query.fetchall())

    # Representation method
    # This will format the output in the correct order
    # Format is @dataclass-style: Classname(attr=value, attr2=value2, ...)
    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()]))

