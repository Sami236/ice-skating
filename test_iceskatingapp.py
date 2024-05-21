from skater import Skater
from event import Event
from track import Track
import pytest

#objects to test with
skater = Skater(10, 'Diane', 'Valkenburg', 'NED', 'F', '1984-08-30')
track = Track(15, 'Ritten Arena', 'Collalbo', 'ITA', 1, 1198)
event = Event(1, '1,500 Meter',	29,	'2003-11-08', 1500, 107.37, 4, 'Erben Wennemars', 'M')

# Test to check if the age of a skater is correct based on the date_of_birth
def test_age_of_skater():
    age = skater.get_age()
    assert age == 39


# Test to check if the amount of events for a specific skater is returned correctly
def test_amount_of_events_of_skater():
    events = skater.get_events()    
    assert len(events) == 6


# Test to check if the amount of events for a specific track is returned correctly
def test_amount_of_events_of_track():
    events = track.get_events()
    assert len(events) == 12


# Test to check if the returned date matches the specified format for that event date
def test_event_date_conversion():
    converted_date = event.convert_date(to_format='%Y-%m')
    assert converted_date == '2003-11'


# Test to check if the duration is converted from 1H19 to the specified format
def test_event_duration_conversion():
    converted_duration = event.convert_duration(to_format='%m')
    assert converted_duration == '01'


# Test to check the amount of skaters on a specified event
def test_amount_of_skaters_on_event():
    skaters = event.get_skaters()
    assert len(skaters) == 56


# Test to validate if the given track of a specified event is correct
def test_track_on_event():
    track = event.get_track()
    assert track[0]._id == 29 and len(track) == 1
