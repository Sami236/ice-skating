import csv
import sys
import os

from to_object import to_track, to_event, to_skater
from event import Event
from skater import Skater
from track import Track
from datetime import datetime

from db import cursor
from config import DATE_FORMAT


def write_csv(file_name, query_result):
    headers = [column[0] for column in cursor.description]
    with open(file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)            
        csv_writer.writerows(query_result)


class Reporter:
    # How many skaters are there? -> int
    def total_amount_of_skaters(self) -> int:
        query = cursor.execute('''
            SELECT COUNT(*)
            FROM skaters
        ''')
        return query.fetchone()[0]

    # What is the highest track? -> Track
    def highest_track(self) -> Track:
        query = cursor.execute('''
            SELECT *
            FROM tracks
            WHERE altitude = (
                SELECT MAX(altitude)
                FROM tracks
            )
        ''')
        return to_track(query.fetchone())

    # What is the longest AND shortest event? -> tuple[Event, Event]
    def longest_and_shortest_event(self) -> tuple[Event, Event]:
        query = cursor.execute('''
            SELECT *
            FROM events
            WHERE id = (
                SELECT id
                FROM events
                WHERE distance = (SELECT MAX(distance) FROM events)
            ) OR id = (
                SELECT id
                FROM events
                WHERE distance = (SELECT MIN(distance) FROM events)
            )
        ''')
        return to_event(query.fetchall())

    # Which event has the most laps for the given track_id -> tuple[Event, ...]
    def events_with_most_laps_for_track(self, track_id: int) -> tuple[Event, ...]:
        query = cursor.execute('''
            SELECT events.*
            FROM events, tracks
            WHERE events.track_id = tracks.id
                AND track_id = ?
                AND laps = (
                    SELECT MAX(laps)
                    FROM events
                    WHERE track_id = ?
                )
        ''', (track_id, track_id,))
        return to_event(query.fetchall())


    # Which skaters have made the most events -> tuple[Skater, ...]
    # Which skaters have made the most succesful events -> tuple[Skater, ...]
    def skaters_with_most_events(self, only_wins: bool = False) -> tuple[Skater, ...]:
        if only_wins:
            data = 'AND winner = first_name || \' \' || last_name'
        else:
            data = ''

        query = cursor.execute('''
            SELECT skaters.*
            FROM skaters
            WHERE skaters.id = (
                SELECT skater_id
                FROM (
                    SELECT COUNT(*) AS 'event_count', skater_id
                    FROM event_skaters, events, skaters
                    WHERE event_skaters.event_id = events.id
                        and skaters.id = event_skaters.skater_id
                        {}
                    GROUP BY skater_id
                    ORDER BY event_count DESC
                    LIMIT 1
                )
            )
        '''.format(data))
        return to_skater(query.fetchall())
    

    # Which track has the most events -> Track
    def tracks_with_most_events(self) -> Track:
        query = cursor.execute('''
            SELECT tracks.*
            FROM tracks, events
            WHERE tracks.id = events.track_id
            GROUP BY tracks.id
            HAVING COUNT(*) = (
                SELECT MAX(event_count) FROM (
                    SELECT COUNT(*) AS 'event_count'
                    FROM events
                    GROUP BY track_id
                )
            )
        ''')
        return to_track(query.fetchone())

    # Which track had the first event? -> Track
    # Which track had the first outdoor event? -> Track
    def get_first_event(outdoor_only: bool = False) -> Track:
        if outdoor_only:
            data = '''
                WHERE outdoor = 1 
                    AND events.track_id = tracks.id
            '''
        else:
            data = ''

        query = cursor.execute('''
            SELECT tracks.*
            FROM tracks, events
            WHERE tracks.id = events.track_id 
                AND date = (
                    SELECT MAX(date)
                    FROM events, tracks
                        {}
                )
            LIMIT 1
        '''.format(data))
        return  to_track(query.fetchone())

    # Which track had the latest event? -> Track
    # Which track had the latetstoutdoor event? -> Track
    def get_latest_event(outdoor_only: bool = False) -> Track:
        if outdoor_only:
            data = '''
                WHERE outdoor = 1 
                    AND events.track_id = tracks.id
            '''
        else:
            data = ''

        query = cursor.execute('''
            SELECT tracks.*
            FROM tracks, events
            WHERE tracks.id = events.track_id 
                AND date = (
                    SELECT MIN(date)
                    FROM events, tracks
                        {}
                )
            LIMIT 1
        '''.format(data))
        return  to_track(query.fetchone())

    # Which skaters have raced track Z between period X AND Y? -> tuple[Skater, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Skaters on Track Z between X AND Y.csv`
    # example: `Skaters on Track Kometa between 2021-03-01 AND 2021-06-01.csv`
    # date input always in format: YYYY-MM-DD
    # otherwise it should just return the value as tuple(Skater, ...)
    # CSV example (this are also the headers):
    #   id, first_name, last_name, nationality, gender, date_of_birth
    def get_skaters_that_skated_track_between(self, track: Track, start: datetime, end: datetime, to_csv: bool = False) -> tuple[Skater, ...]:
        start = start.strftime(DATE_FORMAT)
        end = end.strftime(DATE_FORMAT)

        # Retrieve track name from the database
        track_query = cursor.execute('''
            SELECT name
            FROM tracks
            WHERE id = ?
        ''', (track._id,))
        track_name = track_query.fetchone()[0]

        query = cursor.execute('''
            SELECT skaters.*
            FROM skaters, events, event_skaters
            WHERE skaters.id = event_skaters.skater_id
                AND event_skaters.event_id = events.id
                AND track_id = ?
                AND date BETWEEN ? AND ?
        ''', (track._id, start, end,))
        result = query.fetchall()

        if to_csv:
            file_name = f'Skaters on Track {track_name} between {start} AND {end}.csv'
            write_csv(file_name, result)
        else:
            return to_skater(result)

    # Which tracks are located in country X? ->tuple[Track, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Tracks in country X.csv`
    # example: `Tracks in Country USA.csv`
    # otherwise it should just return the value as tuple(Track, ...)
    # CSV example (this are also the headers):
    #   id, name, city, country, outdoor, altitude
    def get_tracks_in_country(self, country: str, to_csv: bool = False) -> tuple[Track, ...]:
        query = cursor.execute('''
            SELECT tracks.*
            FROM tracks
            WHERE country = ?
        ''', (country,))

        result = query.fetchall()

        if to_csv:
            file_name = f'Tracks in country {country}.csv'
            write_csv(file_name, result)
        else:
            return to_track(result)


    # Which skaters have nationality X? -> tuple[Skater, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Skaters with nationality X.csv`
    # example: `Skaters with nationality GER.csv`
    # otherwise it should just return the value as tuple(Skater, ...)
    # CSV example (this are also the headers):
    #   id, first_name, last_name, nationality, gender, date_of_birth
    def get_skaters_with_nationality(self, nationality: str, to_csv: bool = False) -> tuple[Skater, ...]:
        query = cursor.execute('''
            SELECT skaters.*
            FROM skaters
            WHERE nationality = ?
        ''', (nationality, ))

        result = query.fetchall()

        if to_csv:
            file_name = 'Skaters with nationality {}.csv'.format(nationality)
            write_csv(file_name, result)
        else:
            return to_skater(result)
