def getMaxEventMatch(data):
    event_max = 0
    match_max = 0
    for row in data:
        if row['event_id'] > event_max:
            event_max = row['event_id']
        if row['event_data']['match_id'] > match_max:
            match_max = row['event_data']['match_id']
    return event_max, match_max


def checkEventDataFields(event):
    if event['event_type'] == 'match_start':
        if 'match_id' in event['event_data'] and 'league_id' in event['event_data'] and 'home_club' in event[
            'event_data'] and 'away_club' in event['event_data']:
            if isinstance(event['event_data']['match_id'], (int, type(None))) and isinstance(
                    event['event_data']['league_id'], (int, type(None))) and isinstance(
                    event['event_data']['home_club'], (str, type(None))) and isinstance(
                    event['event_data']['away_club'], (str, type(None))):
                return False
    elif event['event_type'] == 'goal':
        if 'match_id' in event['event_data'] and 'scoring_club' in event['event_data']:
            if isinstance(event['event_data']['match_id'], (int, type(None))) and isinstance(
                    event['event_data']['scoring_club'], (str, type(None))):
                return False
    elif event['event_type'] == 'match_end':
        if 'match_id' in event['event_data']:
            if isinstance(event['event_data']['match_id'], (int, type(None))):
                return False
    return True


def checkGoalTime(event, match_started, match_ended):
    if event['event_type'] != 'goal':
        return False
    if match_started == -1 or match_ended == -1:
        return True
    if event['event_type'] == 'goal' and match_started <= event['event_timestamp'] <= match_ended:
        return False
    return True
