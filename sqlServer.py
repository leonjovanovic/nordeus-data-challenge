import mysql.connector


def createDB(cursor):
    cursor.execute("DROP DATABASE IF EXISTS football_data;")
    cursor.execute("CREATE DATABASE football_data")


def createMatchesTable(cursor):
    cursor.execute(
        "CREATE TABLE `football_data`.`match_start` (`match_id` INT NOT NULL,`league_id` INT NOT NULL,`home_club` VARCHAR(45) NOT NULL, `away_club` VARCHAR(45) NOT NULL,`home_goals` INT,`away_goals` INT, PRIMARY KEY (`match_id`));")


def createGoalTable(cursor):
    cursor.execute(
        "CREATE TABLE `football_data`.`goal` (`event_id` INT NOT NULL,`match_id` INT NOT NULL,`scoring_club` VARCHAR(45) NOT NULL,PRIMARY KEY (`event_id`));")


def insertData(cursor, data):
    i = 0
    for row in data:
        sql = ''
        values = ''
        if row['event_type'] == 'match_start':
            sql = ("INSERT INTO match_start (match_id, league_id, home_club, away_club) VALUES (%s, %s, %s, %s)")
            values = (row['event_data']['match_id'], row['event_data']['league_id'], row['event_data']['home_club'],
                      row['event_data']['away_club'])
        elif row['event_type'] == 'goal':
            sql = ("INSERT INTO goal (event_id, match_id, scoring_club) VALUES (%s, %s, %s)")
            values = (row['event_id'], row['event_data']['match_id'], row['event_data']['scoring_club'])
        cursor.execute(sql, values)
        i += 1


def createScoreTable(cursor):
    cursor.execute("""CREATE TABLE scores AS (SELECT p.match_id, p.league_id, p.home_club, p.away_club, COALESCE(t.home, 0) as "home", COALESCE(t.away, 0) as "away" FROM football_data.match_start as p LEFT OUTER JOIN

                    ((SELECT t1.match_id, home, away
                    FROM (SELECT match_id, COUNT(*) as home FROM football_data.goal WHERE scoring_club="home" GROUP BY match_id) as t1
                    LEFT OUTER JOIN (SELECT match_id, COUNT(*) as away FROM football_data.goal WHERE scoring_club="away" GROUP BY match_id) as t2 ON t1.match_id = t2.match_id)

                    UNION

                    (SELECT t2.match_id, home, away
                    FROM (SELECT match_id, COUNT(*) as home FROM football_data.goal WHERE scoring_club="home" GROUP BY match_id) as t1
                    RIGHT OUTER JOIN (SELECT match_id, COUNT(*) as away FROM football_data.goal WHERE scoring_club="away" GROUP BY match_id) as t2 ON t1.match_id = t2.match_id)

                    ORDER BY match_id) as t
                    
                    ON p.match_id = t.match_id)""")


def createTeamTable(cursor):
    cursor.execute(
        "CREATE TABLE teams AS((SELECT league_id, home_club as club FROM football_data.scores) UNION (SELECT league_id, away_club FROM football_data.scores))")


def createLeaderboardTable(cursor):
    cursor.execute("""CREATE TABLE leaderboard AS (
                    SELECT tt1.league_id, tt1.club, tt1.score, tt2.goals FROM
                    (SELECT t1.league_id, t1.club, t1.points + coalesce(t2.points, 0) as score FROM
                    ((SELECT teams.league_id as league_id, teams.club as club, 3 * COUNT(*) as points FROM scores, teams WHERE scores.home_club = teams.club AND scores.home > scores.away OR scores.away_club = teams.club AND scores.home < scores.away 
                    GROUP BY teams.club) as t1
                    LEFT OUTER JOIN 
                    (SELECT teams.league_id as league_id, teams.club as club, COUNT(*) as points FROM scores, teams WHERE scores.home_club = teams.club AND scores.home = scores.away OR scores.away_club = teams.club AND scores.home = scores.away 
                    GROUP BY teams.club) as t2
                    ON t1.club = t2.club)) as tt1
                    LEFT OUTER JOIN 
                    (SELECT teams.league_id, teams.club, CAST(SUM(CASE WHEN scores.home_club = teams.club THEN scores.home - scores.away ELSE scores.away - scores.home END) AS SIGNED) as goals 
                    FROM scores, teams
                    WHERE scores.home_club = teams.club OR scores.away_club = teams.club
                    GROUP BY teams.club) as tt2
                    ON tt1.club = tt2.club
                    ORDER BY tt1.league_id, tt1.score DESC, tt2.goals DESC, tt1.club)""")


def openConnection(user, password, host):
    try:
        cnx = mysql.connector.connect(user=user, password=password, host=host)
    except mysql.connector.errors.ProgrammingError:
        print("Incorrect login credentials! Try again.")
        return None, None
    cursor = cnx.cursor()
    print("Connection successful!")
    createDB(cursor)
    print("Database created!")
    cnx = mysql.connector.connect(user=user, password=password, host=host, database='football_data')
    cursor = cnx.cursor()
    return cnx, cursor


def closeConnection(cnx):
    cnx.close()


def post(data, cnx, cursor):
    createMatchesTable(cursor)
    createGoalTable(cursor)
    insertData(cursor, data)

    createScoreTable(cursor)
    createTeamTable(cursor)
    createLeaderboardTable(cursor)

    cnx.commit()


def get(league_id, cnx, cursor):
    sql = "SELECT club, score, goals FROM leaderboard WHERE league_id=%s"
    cursor.execute(sql, (league_id,))
    myresult = cursor.fetchall()
    print("Club | Points | Goal difference")
    for x in myresult:
        print(str(x[0]) + " | " + str(x[1]) + " | " + str(x[2]))
    print("")
    return myresult
