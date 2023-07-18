import sqlite3 as sql

def valid_input():
    pass

def add_participation():
    pass

def edit_participation():
    pass

def remove_participation():
    pass

if __name__ == "__main__":
    DATABASE = r"Database file path"
    exit = False

    with sql.connect(DATABASE) as conn:
        cursor = conn.cursor()
        print("Welcome message")

        while True:
            while True:
                action = str(input("Input prompt")).lower()
                if action == "exit":
                    exit = True
                    break
                elif action == "add":
                    add_participation()
                    break
                elif action =="edit":
                    edit_participation()
                    break
                elif action =="remove":
                    remove_participation()
                    break
            if exit: break