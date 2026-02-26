import sqlite3
from datetime import datetime

class Database():

    def __init__(self, file="database/database.db"):
        self.con = sqlite3.connect(file)
        self.cursor = self.con.cursor()

        self.createMessageTable()

        
    # Creates the message table ONLY IF IT DOES NOT EXIST
    def createMessageTable(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS messages(author, message, time);
                            """)
        
        print("LOG: Messages Table created if not exists")

    # DELETES and recreates the message table
    def resetMessageTable(self):
        self.cursor.executescript("""
                            DROP TABLE IF EXISTS messages;
                            CREATE TABLE IF NOT EXISTS messages(author, message, time);
                            """)
        self.con.commit()
        
        print("LOG: Messages Table Reset")

    # Inserts a message into the message table 
    def insertMessage(self, author, message):
        time = datetime.now()
        self.cursor.execute("""
                            INSERT INTO messages VALUES(?, ?, ?); 
                            """, (author, message, time))
        self.con.commit()

        print(f"LOG: Message logged by {author} - '{message}' @ {time}")

    # get the num of messages from author
    def getMessageCount(self, author):
        result = self.cursor.execute("""
                                     SELECT COUNT(*) FROM messages WHERE author = ?;
                                     """, (author,))
        result = self.cursor.fetchone() 
    
        count = result[0] if result else 0
    
        return count