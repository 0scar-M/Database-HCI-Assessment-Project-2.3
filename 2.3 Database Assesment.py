import sqlite3 as sql
import os

def valid_input(prompt, error_prompt, type_, *values):
    """
    Gets input from the user and validates it.
    error_prompt will be shown to the user if they input an incorrect value
    type_ is the type of the input. If it is str then the program will check that input_ is in values.
    """
    while True:
        try:
            input_ = input(prompt)
            if input_ == "exit": exit()
            input_ = type_(input_)
            if type_ == str:
                if input_ not in values[0]: raise
            break
        except Exception:
            print(error_prompt)
    return input_

def get_events_groups():
    """
    Gets the name field from the events table and house+' '+gender from the groups table.
    Runs everytime the user modifies or reads the database.
    """
    global events, groups
    events = [x[0] for x in cursor.execute("SELECT name FROM events ORDER BY id;").fetchall()]
    groups = [x[0] for x in cursor.execute("SELECT house||\' \'||gender FROM groups ORDER BY id;").fetchall()]

def format_list(list_):
    "Formats lists from ['a', 'b', 'c'] to a, b, c"
    return ', '.join(list_).title()

def results():
    pass

def add_participation():
    "Adds a participation for a certain event and group to the participations table in the database."
    get_events_groups()
    
    event_id = events.index(valid_input("Enter the event that you want to add a participation for: ", f"Make sure that you have entered one of these events: {format_list(events)}", str, events))+1 # add one because SQL PKs start at 1 not 0 like Python lists.
    group_id = groups.index(valid_input("Enter the group that you want to add a participation for: ", f"Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    avg_score = valid_input(f"Enter the average score for {groups[group_id-1]}: ", "Please make sure that you entered a valid number.", float, "True")
    
    cursor.execute("INSERT INTO participations VALUES (?, ?, ?);", (event_id, group_id, avg_score))
    conn.commit()

def edit_participation():
    "Edits a participation for a certain event and group in the participations table in the database."
    get_events_groups()

    event_id = events.index(valid_input("What event do you want to change a participation for? ", f"Make sure that you have entered one of these events: {format_list(events)}", str, events))+1
    group_id = groups.index(valid_input("What group do you want to change a participation for? ", f"Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    avg_score = valid_input(f"Enter the new average score for {groups[group_id-1]}: ", "Please make sure that you entered a valid number.", float)
    
    cursor.execute("UPDATE participations SET event_id = ?, group_id = ?, avg_score = ? WHERE event_id = ? AND group_id = ?;", (event_id, group_id, avg_score, event_id, group_id))
    conn.commit()

def remove_participation():
    "Removes a participation for a certain event and group from the participations table in the database."
    get_events_groups()

    event_id = events.index(valid_input("What event do you want to remove a participation for? ", f"Make sure that you have entered one of these events: {format_list(events)}", str, events))+1
    group_id = groups.index(valid_input("What group do you want to remove a participation for? ", f"Make sure that you have entered one of these groups: {format_list(groups)}", str, groups))+1
    
    cursor.execute("DELETE FROM participations WHERE event_id = ? AND group_id = ?;", (event_id, group_id))
    conn.commit()

if __name__ == "__main__":
    DATABASE = os.path.join(os.path.dirname(__file__), r"participation day.db")

    with sql.connect(DATABASE) as conn:
        cursor = conn.cursor()
        print("\nWelcome to the participation day database user interface. To exit the program at any time, enter 'exit'.")

        while True:
            while True:
                action = valid_input("Enter add, edit, remove or results to modify/view the database: ", "Please make sure that you have entered a valid command. ", str, ["add", "edit", "remove", "results"])
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
