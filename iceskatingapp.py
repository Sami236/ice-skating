import os
import sys
import json
import sqlite3

from skater import Skater
from track import Track
from event import Event
from iceskatingreporter import Reporter
from datetime import datetime   
from db import cursor, conn


def insert(table_name: str, data: tuple):
    #insert data from json file into table
    place_holders = '?,'.join(' ' for _ in range(len(data) + 1))[:-2]
    try:
        cursor.execute(f'''
            INSERT INTO {table_name}
            VALUES ({place_holders})
        ''', data)
        conn.commit()
    except Exception:
        pass


def convert_duration(duration: str) -> float:
    if ':' in duration:
        minutes, seconds_with_milliseconds = duration.split(':')
        seconds, milliseconds = seconds_with_milliseconds.split('.')
        
        total_seconds = (int(minutes) * 60) + int(seconds)
        milliseconds = int(milliseconds)
        return float(f'{total_seconds}.{milliseconds}')
    return float(duration)


def insert_json_data():
    with open('events.json', 'r') as file:
        entries = json.loads(file.read())
        
        for event in entries:
            winner_name = f"{event['results'][0]['skater']['firstName']} {event['results'][0]['skater']['lastName']}"
            events_data = (
                event['id'], event['distance']['name'], event['track']['id'],
                event['start'], event['distance']['distance'], convert_duration(event['results'][0]['time']),
                event['distance']['lapCount'], winner_name, event['category'],
            )
            insert('events', events_data)

            #tracks
            track = event['track']
            tracks_data = (
                track['id'], track['name'], track['city'], track['country'],
                track['isOutdoor'], track['altitude'],
            )
            insert('tracks', tracks_data)

            for result in event['results']:
                #skaters
                skater = result['skater']
                skaters_data = (
                    skater['id'], skater['firstName'], skater['lastName'], skater['country'],
                    skater['gender'], skater['dateOfBirth']
                )
                insert('skaters', skaters_data)

                #event_skater
                event_skaters_data = (
                    skater['id'], event['id']
                )
                insert('event_skaters', event_skaters_data)

def print_menu():
    print("\nSelect a query to run:")
    print("1. Total amount of skaters")
    print("2. Highest track")
    print("3. Longest and shortest event")
    print("4. Events with most laps for a track")
    print("5. Skaters with most events (only wins)")
    print("6. Track with most events")
    print("7. Track with first event")
    print("8. Track with latest event")
    print("9. Skaters that skated track between dates")
    print("10. Tracks in country")
    print("11. Skaters with nationality")
    print("12. Exit")


def run_query(choice):
    r = Reporter()
    if choice == 1:
        print("Total amount of skaters:", r.total_amount_of_skaters())
    elif choice == 2:
        print("Highest track:", r.highest_track())
    elif choice == 3:
        longest, shortest = r.longest_and_shortest_event()
        print("Longest event:", longest)
        print("Shortest event:", shortest)
    elif choice == 4:
        track_id = int(input("Enter track ID: "))
        print("Events with most laps for track:", r.events_with_most_laps_for_track(track_id))
    elif choice == 5:
        wins_only = input("Include only wins? (y/n): ").lower() == 'y'
        print("Skaters with most events:", r.skaters_with_most_events(only_wins=wins_only))
    elif choice == 6:
        print("Track with most events:", r.tracks_with_most_events())
    elif choice == 7:
        print("Track with first event:", r.get_first_event())
    elif choice == 8:
        print("Track with latest event:", r.get_latest_event())
    elif choice == 9:
        track_id = int(input("Enter track ID: "))
        start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), '%Y-%m-%d')
        end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), '%Y-%m-%d')
        to_csv = input("Save results to CSV? (y/n): ").lower() == 'y'

        # Retrieve track details from the database
        track_query = cursor.execute('''
            SELECT *
            FROM tracks
            WHERE id = ?
        ''', (track_id,))
        track_data = track_query.fetchone()

        if track_data:
            track = Track(*track_data)  # Create Track object with retrieved track details
            skaters = r.get_skaters_that_skated_track_between(track, start_date, end_date, to_csv=to_csv)
            if not to_csv:
                print("Skaters that skated track between dates:", skaters)
        else:
            print(f"No track found with ID {track_id}.")
    elif choice == 10:
        country = input("Enter country: ")
        to_csv = input("Save results to CSV? (y/n): ").lower() == 'y'
        tracks = r.get_tracks_in_country(country, to_csv=to_csv)  # Pass the to_csv argument correctly
        if not to_csv:
            print("Tracks in country:", tracks)
    elif choice == 11:
        nationality = input("Enter nationality: ")
        to_csv = input("Save results to CSV? (y/n): ").lower() == 'y'
        skaters = r.get_skaters_with_nationality(nationality, to_csv=to_csv)
        if not to_csv:
            print("Skaters with nationality:", skaters)
    elif choice == 12:
        sys.exit()
    else:
        print("Invalid choice")


def main():
    insert_json_data()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear console screen
        print_menu()
        try:
            choice = int(input("Enter your choice: "))
            run_query(choice)
        except ValueError:
            print("Invalid choice. Please enter a number.")
        input("Press Enter to continue...")  # Wait for user to press Enter

if __name__ == "__main__":
    main()
