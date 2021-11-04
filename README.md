# Nordeus - Data Engineering Challenge 2021

## Summary
&nbsp;&nbsp;&nbsp;&nbsp;The goal of this application is to create leaderboard based on input league number and previously generated events. Application consists of two parts: 
  * [Cleaning data from generated events in JSON file](#cleaning-data)
  * [Creating Leaderboard table on MySQL Server](#creating-leaderboard)

&nbsp;&nbsp;&nbsp;&nbsp;Generated data is stored in [events.jsonl]() file. Each row in the file represents one event. Event can either be match start, goal or match end. Each event has multiple fields that describe that event in detail.

## Cleaning data
&nbsp;&nbsp;&nbsp;&nbsp;Data is first imported from JSONL file using [Pandas library](https://pandas.pydata.org/docs/reference/api/pandas.io.json.read_json.html) and converted to list of [dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries). Cleaning process is divided into 4 steps:
  * Deleting duplicate events with same *event_id* field.
  * Deleting events with incorect *event_data* field.
  * Deleting goal events which have incorrect time or dont have corresponding match start/end events.
  * Deleting invalid match start/end event pairs.

&nbsp;&nbsp;&nbsp;&nbsp;Deleting duplicate events is done by creating boolean array with biggest *event_id* number elements. At the beginning every element in array is set to *False*. In first pass throughout data list, each event with first-seen *event_id* will trigger field in *array[event_id]* to *True*. Every next event with *event_id* that already triggered field in array will be added to list for future removal.

---
&nbsp;&nbsp;&nbsp;&nbsp;Detecting and deleting events with incorect *event_data* field is achieved by checking each event (row) in first pass for irregularities. If contents of *event_data* don't have all fields or if any field inside *event_data* isn't correct data type, that event will be flagged for removal. 

---
&nbsp;&nbsp;&nbsp;&nbsp;For deleting invalid goal events we had to create two additional arrays. Each array will, at the end of first pass, have timestamps of match start and match end. Row number in the arrays corresponds to *match_id*, similar to *event_id array*. In second pass we check each goal event timestamp to see if its between match start and match end timestamp. If not, those events will be removed at the end of the second pass.

---
&nbsp;&nbsp;&nbsp;&nbsp;Last step is deleting ivalid match start/end event pairs, which is done by checking above mentioned match arrays to see if there is any index that exists in one and does not exists in other array. If there is such case, *match_id* is flagged and during second pass every event with that *match_id* will be removed.

## Creating Leaderboard
&nbsp;&nbsp;&nbsp;&nbsp;
