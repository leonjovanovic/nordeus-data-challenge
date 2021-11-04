import utilities


def cleanData(data):
    # Finding max event_id and match_id number so we can create arrays with sufficient number of elements for each array
    EVENT_ID_MAX, MATCH_ID_MAX = utilities.getMaxEventMatch(data)
    duplicates_arr = [False] * (EVENT_ID_MAX + 1)
    match_start_arr = [-1] * (MATCH_ID_MAX + 1)
    match_end_arr = [-1] * (MATCH_ID_MAX + 1)
    # Every incorrect event (its row index in data) will be added to delete_arr for future removal
    delete_arr = []
    i = 0
    for row in data:
        # --------------------------- I Detect duplicates ---------------------------
        # duplicates_arr elements will trigger to True at first unique event_id, every next (duplicate) will be removed
        if duplicates_arr[row['event_id']]:
            delete_arr.append(i)
            i += 1
            continue
        else:
            duplicates_arr[row['event_id']] = True
        # ---------------------------------------------------------------------------
        # ----------------- II Detect incorrect fields in event_data ----------------
        if utilities.checkEventDataFields(row):
            delete_arr.append(i)
            i += 1
            continue
        # ---------------------------------------------------------------------------
        # Store match start and end timestamps so every goal event in next pass can check if its time is between
        # coresponding match start and end events.
        if row['event_type'] == 'match_start':
            match_start_arr[row['event_data']['match_id']] = row['event_timestamp']
        if row['event_type'] == 'match_end':
            match_end_arr[row['event_data']['match_id']] = row['event_timestamp']
        i += 1
    # Delete first batch of incorrect data
    for d in sorted(delete_arr, reverse=True):
        del (data[d])
    # ------------- IV Detect non valid match start/end event pairs -------------
    i = 0
    match_ids = []
    for start, end in zip(match_start_arr, match_end_arr):
        if start == -1 and end != -1 or start != -1 and end == -1 or end < start and end != -1:
            match_ids.append(i)
        i += 1
    # ---------------------------------------------------------------------------
    delete_arr = []
    i = 0
    for row in data:
        # Delete detected non valid match start/end events
        if row['event_data']['match_id'] in match_ids:
            delete_arr.append(i)
            i += 1
            continue
        # --------------------- III Detect incorrect goal time ----------------------
        if row['event_type'] == 'goal':
            if utilities.checkGoalTime(row, match_start_arr[row['event_data']['match_id']],
                                       match_end_arr[row['event_data']['match_id']]):
                delete_arr.append(i)
        # ---------------------------------------------------------------------------
        i += 1
    # Delete second batch of incorrect data
    for d in sorted(delete_arr, reverse=True):
        data.remove(data[d])

    return data
