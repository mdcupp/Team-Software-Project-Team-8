import sqlite3
from datetime import datetime

class Database():

    def __init__(self, file="database/database.db"):
        self.con = sqlite3.connect(file)
        self.cursor = self.con.cursor()

        self.createMessageTable()
        self.createReactionTable()

        
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
                            """, (author.id, message, time))
        self.con.commit()

        print(f"LOG: Message logged by {author} - '{message}' @ {time}")

    # get the num of messages from author id
    def getMessageCount(self, author_id):
        result = self.cursor.execute("""
                                     SELECT COUNT(*) FROM messages WHERE author = ?;
                                     """, (author_id,))
        result = self.cursor.fetchone() 
    
        count = result[0] if result else 0
    
        return count

    # Create reaction table if it doesn't exist
    def createReactionTable(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS reactions(emoji, sender, receiver, message_id, time);
                            """)

        print("LOG: Reactions Table created if not already existing")

    # Reset reaction table
    def resetReactionTable(self):
        self.cursor.executescript("""
                                  DROP TABLE IF EXISTS reactions;
                                  CREATE TABLE IF NOT EXISTS reactions(emoji, sender, receiver, message_id, time);
                                  """)
        self.con.commit()

        print("LOG: Reactions Table reset")

    # Insert log of reaction into table
    def insertReaction(self, emoji, sender_id, receiver_id, message_id):
        time = datetime.now()

        self.cursor.execute("""
                            INSERT INTO reactions VALUES(?, ?, ?, ?, ?);
                            """, (emoji, sender_id, receiver_id, message_id, time))

        self.con.commit()

        print(f"LOG: Reaction {emoji} sent by {sender_id} to {receiver_id}")

    # Get reaction count for a given user
    def getReactionCount(self, author_id):
        result = self.cursor.execute("""
                                     SELECT COUNT(*) FROM reactions WHERE author = ?;
                                     """, (author_id,))
        result = self.cursor.fetchone()

        count = result[0] if result else 0

        return count
