import sqlite3

def get_connection():
    """
    Creates and returns a connection to the SQLite database file.
    All query files (user_queries.py, parking_queries.py) call this 
    function to interact with the same data source.
    """
    # The string 'database.db' must match the filename you created
    return sqlite3.connect('database.db')