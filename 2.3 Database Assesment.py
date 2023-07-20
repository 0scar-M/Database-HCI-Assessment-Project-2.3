import sqlite3 as sql
import os

def valid_input(prompt, error_prompt, type_, values):
    while True:
        try:
            input_ = type_(input(prompt))
            if input_ not in values: raise
            break
        except Exception:
            print(error_prompt)
    return input_

def results():
    pass

def add_participation():
    pass

def edit_participation():
    pass

def remove_participation():
    pass

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
