import sqlite3 as sql
import os
import numpy as np

def valid_input(prompt, error_prompt, type_, *values):
    """
    Gets input from the user and validates it.
    error_prompt will be shown to the user if they input an incorrect value
    type_ is the type of the input. If it is str then the program will check that input_ is in values.
    """
    while True:
        try:
            input_ = input(prompt)
            if input_ == "exit": exit() # check for exit input before type_(input_) so that if they entered exit in a numeric input field it doesn't raise an error.
            input_ = type_(input_)
            if type_ == str:
                if input_ not in values[0]: raise # only check for input_ in values[0] after you know they have entered a string because if type_ == int or float then values will be empty.
            break
        except Exception: # exit() raises SystemExit but except Exception: fixes that for some reason.
            print(error_prompt)
    return input_

def get_events_groups():
    """
    Gets the name field from the events table and house+' '+gender from the groups table.
    Runs everytime the user modifies or reads the database.
    """
    global events, groups
    events = [x[0] for x in cursor.execute("SELECT name FROM events ORDER BY id;").fetchall()]
    groups = [x[0] for x in cursor.execute("SELECT house||' '||gender FROM groups ORDER BY id;").fetchall()]

def format_list(list_):
    "Formats lists from ['a', 'b', 'c'] to 'a, b, c'"
    return ", ".join(list_).title()

def print_results(header, results):
    "Formats and prints results from the database to be displayed to the user."
    results = [header] + [[str(i) for i in x] for x in results] # convert any int/float values in results to str so join works and add column_names to the top of the list.
    max_entry = [max([len(i) for i in x]) for x in np.array(results).T.tolist()] # for each column in results get the length of the longest value in it.
    for x in range(len(results)):
        for i in range(len(results[x])):
            results[x][i] = results[x][i].ljust(max_entry[i], " ") # add spaces at the end of each "cell" to make all cells in a column the same length.        
        print(" │ ".join(results[x])) # column border.
        if x == 0:
            print("─┼─".join(["".ljust(max_entry[i], "─") for i in range(len(results[x]))])) # header-data border

def results():
    """
    Allows users to get data from the database.
    Users can get the winner of each event, the winner of all events or how many events each house won.
    """
    get_events_groups()
    action = valid_input(" │ Enter the name of an event to get all of its participations, 'all' to find the winner of each event or 'overall' to find the overall winner of participation day:\n │ >> ", " │ Please ensure that you have entered a valid event, 'all' or 'overall'.", str, events+["all", "overall"])
    
    if action in events:
        event_index = events.index(action)+1
        event_units = cursor.execute("SELECT units FROM events WHERE events.id = ?", (event_index,)).fetchall()[0][0]
        results = [list(x) for x in cursor.execute("SELECT g.house ||' '|| g.gender AS [group], MIN(p.avg_score) AS score FROM events AS e, participations AS p, [groups] AS g INNER JOIN events ON e.id = p.event_id INNER JOIN [groups] ON g.id = p.group_id WHERE e.id = ? GROUP BY [group] ORDER BY score;", (event_index,)).fetchall()]
        if event_units != "seconds":
            results.reverse()

        print_results(["group", f"average score ({event_units})"], results)

    elif action == "all":
        results = [list(x) for x in cursor.execute("SELECT e.name AS event, g.house ||' '|| g.gender AS winner, MIN(p.avg_score) ||' '|| e.units AS score FROM events AS e, [groups] AS g, participations AS p INNER JOIN events ON e.id = p.event_id INNER JOIN [groups] ON g.id = p.group_id WHERE e.units = 'seconds' GROUP BY e.id UNION ALL SELECT e.name AS event, g.house ||' '|| g.gender AS winner, MAX(p.avg_score) ||' '|| e.units AS score FROM events AS e, [groups] AS g, participations AS p INNER JOIN events ON e.id = p.event_id INNER JOIN [groups] ON g.id = p.group_id WHERE e.units != 'seconds' GROUP BY e.id;").fetchall()]
        
        print_results(["event", "winner", "average score"], results)

    elif action == "overall":
        raw_results = [x[0] for x in cursor.execute("SELECT g.house AS house, MIN(p.avg_score) ||' '|| e.units AS score FROM events AS e, [groups] as g, participations AS p INNER JOIN events ON e.id = p.event_id INNER JOIN [groups] ON g.id = p.group_id WHERE e.units = 'seconds' GROUP BY e.id UNION ALL SELECT g.house AS house, MAX(p.avg_score) ||' '|| e.units AS score FROM events AS e, [groups] as g, participations AS p INNER JOIN events ON e.id = p.event_id INNER JOIN [groups] ON g.id = p.group_id WHERE e.units != 'seconds' GROUP BY e.id ORDER BY house;").fetchall()]
        raw_results = [[x, raw_results.count(x)] for x in raw_results]
        results = []
        [results.append(x) for x in raw_results if x not in results] # remove all similar values in list.
        results = [[x, 0] for x in [x[0] for x in cursor.execute("SELECT house FROM groups GROUP BY house").fetchall()] if x not in [x[0] for x in results]] + results # add in the other houses if they aren't already in results
        results.reverse()
        
        print_results(["house", "events won"], results)

def add_participation():
    "Adds a participation for a certain event and group to the participations table in the database."
    get_events_groups()
    
    event_id = events.index(valid_input(" │ Enter the event that you want to add a participation for:\n │ >> ", f" │ Make sure that you have entered one of these events: {format_list(events)}", str, events))+1 # add one because SQL PKs start at 1 not 0 like Python lists.
    group_id = groups.index(valid_input(" │ Enter the group that you want to add a participation for:\n │ >> ", f" │ Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    avg_score = valid_input(f" │ Enter the average score for {groups[group_id-1]}:\n │ >> ", " │ Please make sure that you entered a valid number.", float)
    
    cursor.execute("INSERT INTO participations VALUES (?, ?, ?);", (event_id, group_id, avg_score))
    conn.commit()
    print("Succesfully added participation to database.")

def edit_participation():
    "Edits a participation for a certain event and group in the participations table in the database."
    get_events_groups()

    event_id = events.index(valid_input(" │ What event do you want to change a participation for?\n │ >> ", f" │ Make sure that you have entered one of these events: {format_list(events)}", str, events))+1
    group_id = groups.index(valid_input(" │ What group do you want to change a participation for?\n │ >> ", f" │ Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    avg_score = valid_input(f" │ Enter the new average score for {groups[group_id-1]}:\n │ >> ", " │ Please make sure that you entered a valid number.", float)
    
    cursor.execute("UPDATE participations SET event_id = ?, group_id = ?, avg_score = ? WHERE event_id = ? AND group_id = ?;", (event_id, group_id, avg_score, event_id, group_id))
    conn.commit()

def remove_participation():
    "Removes a participation for a certain event and group from the participations table in the database."
    get_events_groups()

    event_id = events.index(valid_input(" │ What event do you want to remove a participation for?\n │ >> ", f" │ Make sure that you have entered one of these events: {format_list(events)}", str, events))+1
    group_id = groups.index(valid_input(" │ What group do you want to remove a participation for?\n │ >> ", f" │ Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    
    cursor.execute("DELETE FROM participations WHERE event_id = ? AND group_id = ?;", (event_id, group_id))
    conn.commit()

if __name__ == "__main__":
    DATABASE = os.path.join(os.path.dirname(__file__), r"participation day.db")

    with sql.connect(DATABASE) as conn:
        cursor = conn.cursor()
        print("\nWelcome to the participation day database user interface. To exit this program at any time, enter 'exit'.")

        while True:
            while True:
                action = valid_input("\nEnter add, edit, remove or results to modify/view the database: ", "Please make sure that you have entered a valid command. ", str, ["add", "edit", "remove", "results"])
                if action == "results":
                    results()
                    break
                elif action == "add":
                    add_participation()
                    break
                elif action == "edit":
                    edit_participation()
                    break
                elif action == "remove":
                    remove_participation()
                    break
