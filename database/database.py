import sqlite3
from datetime import datetime

class Database():

    def __init__(self, file="database/database.db"):
        self.con = sqlite3.connect(file)
        self.cursor = self.con.cursor()

        self.createMessageTable()
        self.createReactionTable()
        self.createActivityTable()
        self.createMemberEventsTable()
        self.createUsersTable()
        
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

    # Get reaction count for a given user and an emoji
    def getReactionCount(self, user_id, emoji):
        sent_query = """
                     SELECT COUNT(*) FROM reactions WHERE sender = ? AND emoji = ?;
                     """

        received_query = """
                         SELECT COUNT(*) FROM reactions WHERE receiver = ? AND emoji = ?;
                         """

        sent = self.cursor.execute(sent_query, (user_id, emoji)).fetchone()[0]
        received = self.cursor.execute(received_query, (user_id, emoji)).fetchone()[0]

        return sent, received
    
    # Get leaderboard of given reaction
    def getReactionLeaderboard(self, emoji, sentOrReceived):
        if (sentOrReceived == 'sent'):
            query = """
                    SELECT sender, COUNT(*) 
                    FROM reactions 
                    WHERE emoji = ?
                    GROUP BY sender
                    ORDER BY sender ASC
                    LIMIT 45;
                    """
        else:
            query = """
                    SELECT receiver, COUNT(*) 
                    FROM reactions 
                    WHERE emoji = ?
                    GROUP BY receiver
                    ORDER BY receiver ASC
                    LIMIT 45;
                    """

        result = self.cursor.execute(query, (emoji)).fetchall()
        return result

    # Create activity table if it doesn't exist
    def createActivityTable(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS activity(user, activity, seconds);
                            """)

        print("LOG: Activity Table created if not already existing")

    # Reset activity table
    def resetActivityTable(self):
        self.cursor.executescript("""
                                  DROP TABLE IF EXISTS activity;
                                  CREATE TABLE IF NOT EXISTS activity(user, activity, seconds);
                                  """)
        self.con.commit()

        print("LOG: Activity Table reset")

    # Insert activity into table
    def insertActivity(self, user, activity, seconds):
        # Check if this activity has been logged before
        exists = self.cursor.execute("""
                            SELECT COUNT(*) FROM activity WHERE user = ? AND activity = ?;
                            """, (user, activity)).fetchone()[0]

        if exists == 0:
            # Activity has not been logged before
            self.cursor.execute("""
                            INSERT INTO activity VALUES(?, ?, ?);
                            """, (user, activity, seconds))
        else:
            # Activty HAS been logged before
            self.cursor.execute("""
                            UPDATE activity SET seconds = seconds + ? WHERE user = ? and activity = ?;
                            """, (seconds, user, activity))
        

        self.con.commit()

        print(f"LOG: Activity {activity} - {seconds}s by {user}")

    # Get the activity time in seconds for a given user
    def getActivityTime(self, user):
        result = self.cursor.execute("""
                     SELECT activity, seconds FROM activity WHERE user = ? ORDER BY seconds DESC;
                     """, (user)).fetchall()

        return result

    # Create member events table ONLY IF IT DOESNT EXIST
    def createMemberEventsTable(self):
       self.cursor.execute("""
                           CREATE TABLE IF NOT EXISTS member_events(
                           user_id, username, event_type, time
                           );
                       """)
       self.con.commit()
       print("LOG: Member Events Table created")

    def resetEventTable(self):
       self.cursor.executescript("""
                                 DROP TABLE IF EXISTS member_events;
                                 CREATE TABLE IF NOT EXISTS member_events(user_id, username, event_type, time);
                                 """)
       self.con.commit()

       print("LOG: Event Table reset")

    # Insert join into member events table
    def insertJoin(self, user_id, username):
       time = datetime.now()
       self.cursor.execute("""
                           INSERT INTO member_events VALUES(?, ?, ?, ?);
                           """, (user_id, username, "join", time))
       self.con.commit()
 
    # Insert leave into member events table
    def insertLeave(self, user_id, username):
       time = datetime.now()
       self.cursor.execute("""
                           INSERT INTO member_events VALUES(?, ?, ?, ?);
                           """, (user_id, username, "leave", time))
       self.con.commit()
 
    # Get history of joins/leaves for some user
    def getMemberHistory(self, user_id):
       return self.cursor.execute("""
                                  SELECT event_type, time
                                  FROM member_events
                                  WHERE user_id = ?
                                  ORDER BY time DESC;
                                  """, (user_id,)).fetchall()

    # ---------- User Tracking ----------
    # Creates the users table ONLY IF IT DOES NOT EXIST
    def createUsersTable(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users(userId, username, displayName, joinDate);
                            """)
        
        print("LOG: Users Table created if not exists")

    # DELETES and recreates the users table
    def resetUsersTable(self):
        self.cursor.executescript("""
                            DROP TABLE IF EXISTS users;
                            CREATE TABLE IF NOT EXISTS users(userId, username, displayName, joinDate);
                            """)
        self.con.commit()
        
        print("LOG: Users Table Reset")

    # Inserts a user into the users table 
    def insertUser(self, userId, username, displayName, joinDate):
        # time = datetime.now()
        self.cursor.execute("""
                            INSERT INTO users VALUES(?, ?, ?, ?); 
                            """, (userId, username, displayName, joinDate))
        self.con.commit()

        print(f"LOG: User Added \n  ID: {userId}\n  Username: {username}\n  Display Name: {displayName}\n  Join Date: {joinDate}")

    # returns true if the user exists in the table already
    def isUserTracked(self, userId):
        result = self.cursor.execute("""
                                     SELECT COUNT(*) FROM users WHERE userId = ?;
                                     """, (userId,))
        result = self.cursor.fetchone()

        if result[0] == 1:
            return True
        else:
            return False

    # get the user information from username
    def getUserInfo(self, username):
        result = self.cursor.execute("""
                                     SELECT * FROM users WHERE username = ?;
                                     """, (username,))
        result = self.cursor.fetchone() 
    
        return result

