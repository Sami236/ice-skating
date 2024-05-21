from datetime import date
from skater import Skater

from datetime import datetime, timedelta
from db import conn, cursor
from config import DATE_FORMAT, DURATION_FORMAT
from to_object import to_track, to_skater


class Event:

    def __init__(self, id : int, name : str, track_id: int, date : date, distance: int, duration : float, laps : int, winner: str, category: str) -> None:
        self._id = id
        self._name = name
        self._track_id = track_id
        self._date = date
        self._distance = distance
        self._duration = duration
        self._laps = laps
        self._winner = winner
        self._category = category

    def add_skater(self, skater: Skater) -> None:
        cursor.execute('''
            INSERT INTO skaters 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                skater._id, skater._first_name, skater._last_name, 
                skater._nationality, skater._gender, skater._date_of_birth
            )
        )
        conn.commit()

    def get_skaters(self) -> list:
        query = cursor.execute('''
            SELECT skaters.*
            FROM event_skaters, skaters
            WHERE event_id = ?
                AND skater_id = skaters.id
        ''', (self._id,))
        return to_skater(query.fetchall())

    def get_track(self):
        query = cursor.execute('''
            SELECT tracks.*
            FROM tracks, events
            WHERE tracks.id = events.track_id
                AND tracks.id = ?
            LIMIT 1
        ''', (self._track_id,))
        return to_track(query.fetchall())

    def convert_date(self, to_format: str) -> str:
        if type(self._date) == str:
            self._date = datetime.strptime(self._date, DATE_FORMAT)
        return self._date.strftime(to_format)

    def convert_duration(self, to_format: str) -> str:
        seconds = int(float(self._duration))
        milliseconds = int((self._duration - seconds) * 1000)
        duration = timedelta(seconds=seconds, milliseconds=milliseconds)
        base_date = datetime(2000, 1, 1)
        result_datetime = base_date + duration
        return result_datetime.strftime(to_format)

    # Representation method
    # This will format the output in the correct order
    # Format is @dataclass-style: Classname(attr=value, attr2=value2, ...)
    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()]))


