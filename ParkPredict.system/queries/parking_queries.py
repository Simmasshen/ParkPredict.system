import sqlite3

def init_db():
    # This creates 'database.db' if it doesn't exist and connects to it
    conn = sqlite3.connect('database.db')
    
    with open('schema.sql', 'r') as f:
        schema_script = f.read()
    
    with open('seed.sql', 'r') as f:
        seed_script = f.read()
    
    cursor = conn.cursor()
    
    # Execute the schema to create tables
    cursor.executescript(schema_script)
    
    # Execute the seed to add initial data
    cursor.executescript(seed_script)
    
    conn.commit()
    conn.close()
    print("Database created and seeded successfully!")

if __name__ == "__main__":
    init_db()