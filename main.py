import pandas.io.json as pd
import cleanData
import sqlServer

if __name__ == '__main__':
    print("Welcome!")
    # Importing events.json into Pandas DataFrame
    jsonObj = pd.read_json(path_or_buf="events.jsonl", lines=True)
    # Converting DataFrame to Python dictionary
    data = jsonObj.to_dict('records')
    # Removing incorrect data
    data = cleanData.cleanData(data)
    print("Input MySQL Server information")
    cnx, cursor = None, None
    while cnx is None:
        print("Enter username: ")
        username = str(input())
        print("Enter password: ")
        password = str(input())
        print("Enter host:")
        host = str(input())
        # Opening connection with SQL Server
        cnx, cursor = sqlServer.openConnection(user=username, password=password, host=host)
    # Creating SQL database and necessary tables from imported JSON file
    sqlServer.post(data, cnx, cursor)
    print("Leaderboard created!")
    league_id = 0
    while not league_id == -1:
        print("Enter league number: (-1 for exit)")
        try:
            league_id = int(input())
        except ValueError:
            print("League number must be integer from 1 to 8!")
            continue
        # Fetching leaderboard of requested league (int as input). Output is sorted list of tuples.
        leaderboard = sqlServer.get(league_id, cnx, cursor)
    # Closing connection with SQL Server
    sqlServer.closeConnection(cnx)
