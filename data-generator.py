import uuid
import time
from datetime import datetime


import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="myuser",
    password="mypassword",
    database="mydb"
)

# Create a cursor object
cursor = conn.cursor()

# Define the table name
table_name = "event"

# Insert data every second
while True:
    
    # Generate a random string
    data = str(uuid.uuid4())

    # Get the current timestamp
    timestamp = datetime.now()

    query = f"INSERT INTO {table_name} (data, timestamp) VALUES (%s, %s)"
    cursor.execute(query,  (data, timestamp))
        
    # Commit the changes
    conn.commit()
        
    time.sleep(1)
