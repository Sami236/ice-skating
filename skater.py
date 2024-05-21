from datetime import date, datetime
from db import cursor
from config import DATE_FORMAT
from to_object import to_event


class Skater:

    def __init__(self, id:int, first_name: str, last_name: str, nationality: str, gender: str, date_of_birth: str) -> None:
        self._id = id
        self._first_name = first_name
        self._last_name = last_name
        self._nationality = nationality
        self._gender = gender
        self._date_of_birth = date_of_birth

    def get_age(self, date: date = datetime.now()) -> int:
        date_of_birth = datetime.strptime(self._date_of_birth, DATE_FORMAT)
        age = date - date_of_birth
        age = age.days // 365
        return age

    def get_events(self) -> list:
        result = cursor.execute('''
            SELECT events.*
            FROM event_skaters, events
            WHERE skater_id = ?
                AND event_id = events.id
        ''', (self._id,))
        return to_event(result.fetchall())

    # Representation method
    # This will format the output in the correct order
    # Format is @dataclass-style: Classname(attr=value, attr2=value2, ...)
    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()]))

