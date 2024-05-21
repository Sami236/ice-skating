# imports located inside functions to avoid circular import errors
# converts results retrieved from database queries into objects

def to_track(attrs: tuple | list):
    from track import Track
    if type(attrs) == list:
        return tuple([Track(*row) for row in attrs]) 
    return Track(*attrs)

def to_event(attrs: tuple | list):
    from event import Event
    if type(attrs) == list:
        return tuple([Event(*row) for row in attrs]) 
    return Event(*attrs)

def to_skater(attrs: tuple | list):
    from skater import Skater
    if type(attrs) == list:
        return tuple([Skater(*row) for row in attrs]) 
    return Skater(*attrs)