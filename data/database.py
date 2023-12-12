import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Coins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coins (
                user TEXT,
                guild TEXT,
                coins INTEGER,
                PRIMARY KEY (user, guild)
            )
        ''')
        # Daily rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_rewards (
                user TEXT,
                guild TEXT,
                last_claimed TEXT,
                PRIMARY KEY (user, guild)
            )
        ''')
        # Weekly rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_rewards (
                user TEXT,
                guild TEXT,
                last_claimed TEXT,
                PRIMARY KEY (user, guild)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS school (
                user TEXT,
                guild TEXT,
                schoolType TEXT,
                progress INTEGER,
                lastWentToSchoolDate TEXT,
                PRIMARY KEY (user, guild)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                user TEXT,
                guild TEXT,
                job TEXT,
                date_got_job TEXT,
                last_worked TEXT,
                amount_worked INTEGER DEFAULT 0,
                PRIMARY KEY (user, guild)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GuildInfo (
                GuildID TEXT PRIMARY KEY,
                TicketCategoryChannelID TEXT,
                SuggestionCategoryID TEXT,
                SuggestionsChannelID TEXT,
                AcceptedSuggestionsChannelID TEXT,
                DeniedSuggestionsChannelID TEXT,
                ImplementedSuggestionsChannelID TEXT,
                ModCommandsChannelID TEXT,
                ApplicationCategoryID TEXT,
                LogChannelID TEXT,
                BugCategoryID TEXT,
                BugPendingChannelID TEXT,
                BugsAcceptedChannelID TEXT,
                BugsDeniedChannelID TEXT,
                BugsFixedChannelID TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GuildFeatures (
                GuildID TEXT PRIMARY KEY,
                Ticket BOOLEAN DEFAULT TRUE,
                Suggestion BOOLEAN DEFAULT TRUE,
                Application BOOLEAN DEFAULT TRUE,
                Bugs BOOLEAN DEFAULT TRUE,
                Log BOOLEAN DEFAULT TRUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suggestions (
                SuggestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                GuildID TEXT,
                ChannelID TEXT,
                MessageID TEXT,
                AuthorID TEXT,
                SuggestionText TEXT,  -- New column for suggestion text
                Status TEXT  -- 'accepted', 'denied', 'implemented', or NULL/empty
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bugs (
                BugID INTEGER PRIMARY KEY AUTOINCREMENT,
                GuildID TEXT,
                ReporterID TEXT,
                MessageID TEXT,
                ChannelID TEXT,
                BugDescription TEXT,
                Status TEXT  -- 'pending', 'accepted', 'denied', 'fixed'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Applications (
                ApplicationID INTEGER PRIMARY KEY AUTOINCREMENT,
                GuildID TEXT,
                AppName TEXT,
                UserID TEXT,
                ChannelID TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ApplicationReviewMessages (
                GuildID TEXT,
                ChannelID TEXT,
                MessageID TEXT,
                ApplicationID INTEGER,
                PRIMARY KEY (GuildID, ChannelID, MessageID)
            )
        ''')
        conn.commit()
        conn.close()
        
        
    def get_coins(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT coins FROM coins WHERE user = ? AND guild = ?', (user, guild))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    def set_coins(self, user, guild, coins):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO coins (user, guild, coins) VALUES (?, ?, ?)
            ON CONFLICT(user, guild) DO UPDATE SET coins = excluded.coins
        ''', (user, guild, coins))
        conn.commit()
        conn.close()
        
    def get_daily_reward(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_claimed FROM daily_rewards WHERE user = ? AND guild = ?', (user, guild))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_daily_reward(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_rewards (user, guild, last_claimed) VALUES (?, ?, ?)
            ON CONFLICT(user, guild) DO UPDATE SET last_claimed = excluded.last_claimed
        ''', (user, guild, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    # Weekly rewards methods
    def get_weekly_reward(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_claimed FROM weekly_rewards WHERE user = ? AND guild = ?', (user, guild))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_weekly_reward(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weekly_rewards (user, guild, last_claimed) VALUES (?, ?, ?)
            ON CONFLICT(user, guild) DO UPDATE SET last_claimed = excluded.last_claimed
        ''', (user, guild, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
    # Database method to get top coin holders
    def get_top_coins(self, start, end):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user, guild, coins FROM coins ORDER BY coins DESC LIMIT ? OFFSET ?", (end - start, start))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_unique_users_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT user) FROM coins")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_school_info(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT schoolType, progress, lastWentToSchoolDate FROM school WHERE user = ? AND guild = ?', (user, guild))
        result = cursor.fetchone()
        conn.close()
        return result

    def set_school_info(self, user, guild, school_type, progress, last_date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO school (user, guild, schoolType, progress, lastWentToSchoolDate) 
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user, guild) 
            DO UPDATE SET 
                schoolType = excluded.schoolType, 
                progress = excluded.progress, 
                lastWentToSchoolDate = excluded.lastWentToSchoolDate
        ''', (user, guild, school_type, progress, last_date))
        conn.commit()
        conn.close()
    # Method to get job info
    def get_job_info(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT job, date_got_job, last_worked, amount_worked FROM jobs WHERE user = ? AND guild = ?', (user, guild))
        result = cursor.fetchone()
        conn.close()
        return result

    # Method to set job info
    def set_job_info(self, user, guild, job, date_got_job, last_worked, amount_worked):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (user, guild, job, date_got_job, last_worked, amount_worked) 
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user, guild) 
            DO UPDATE SET 
                job = excluded.job, 
                date_got_job = excluded.date_got_job,
                last_worked = excluded.last_worked,
                amount_worked = excluded.amount_worked
        ''', (user, guild, job, date_got_job, last_worked, amount_worked))
        conn.commit()
        conn.close()
        
    def remove_job(self, user, guild):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE user = ? AND guild = ?", (user, guild))
        conn.commit()
        conn.close()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    def get_guild_info(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM GuildInfo WHERE GuildID = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    # Method to set or update guild info
    def set_guild_info(self, guild_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Prepare the columns and values for the SQL query
        columns = ', '.join(f"{key}" for key in kwargs)
        placeholders = ', '.join('?' for _ in kwargs)
        values = list(kwargs.values())

        # The query requires guild_id as the first value and again at the end for the UPDATE part
        sql = f'''
            INSERT INTO GuildInfo (GuildID, {columns}) 
            VALUES (?, {placeholders})
            ON CONFLICT(GuildID) DO UPDATE SET {', '.join(f'{key} = ?' for key in kwargs)}
        '''
        cursor.execute(sql, [guild_id] + values + values)
        conn.commit()
        conn.close()
    
        
    # Method to get guild features
    def get_guild_features(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM GuildFeatures WHERE GuildID = ?', (guild_id,))
        result = cursor.fetchone()
        if not result:
            # If no entry exists, create a default one
            cursor.execute('INSERT INTO GuildFeatures (GuildID) VALUES (?)', (guild_id,))
            conn.commit()
            cursor.execute('SELECT * FROM GuildFeatures WHERE GuildID = ?', (guild_id,))
            result = cursor.fetchone()
        conn.close()
        
        # Convert the tuple result to a dictionary
        if result:
            columns = ["GuildID", "Ticket", "Suggestion", "Application", "Bugs", "Log"]
            return dict(zip(columns, result))
        else:
            return {}
        
        
    def get_all_guild_info(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM GuildInfo WHERE GuildID = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        else:
            return {}
        
        
        
    # Method to set a guild feature
    def set_guild_feature(self, guild_id, feature, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO GuildFeatures (GuildID, {feature}) 
            VALUES (?, ?)
            ON CONFLICT(GuildID) DO UPDATE SET {feature} = ?
        ''', (guild_id, value, value))
        conn.commit()
        conn.close()




    def add_suggestion(self, guild_id, channel_id, message_id, author_id, suggestion_text):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Suggestions (GuildID, ChannelID, MessageID, AuthorID, SuggestionText, Status) 
            VALUES (?, ?, ?, ?, ?, NULL)
        ''', (guild_id, channel_id, message_id, author_id, suggestion_text))
        conn.commit()
        conn.close()

    # Method to update the status and votes of a suggestion
    def update_suggestion(self, suggestion_id, status, new_channel_id=None, new_message_id=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if new_channel_id and new_message_id:
            cursor.execute('''
                UPDATE Suggestions
                SET Status = ?, ChannelID = ?, MessageID = ?
                WHERE SuggestionID = ?
            ''', (status, new_channel_id, new_message_id, suggestion_id))
        else:
            cursor.execute('''
                UPDATE Suggestions
                SET Status = ?
                WHERE SuggestionID = ?
            ''', (status, suggestion_id))

        conn.commit()
        conn.close()
        
    def get_next_suggestion_id(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(SuggestionID) FROM Suggestions')
        result = cursor.fetchone()
        conn.close()

        # If there are no suggestions yet, start from 1
        if result[0] is None:
            return 1
        else:
            return result[0] + 1
        
    def get_suggestion_by_id(self, suggestion_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Suggestions WHERE SuggestionID = ?', (suggestion_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            # Updated columns list to match the current table structure
            columns = ["SuggestionID", "GuildID", "ChannelID", "MessageID", "AuthorID", "SuggestionText", "Status"]
            return dict(zip(columns, result))
        return None


    #Bug Methods
    
    # Method to add a bug report
    def add_bug(self, guild_id, reporter_id, message_id, channel_id, bug_description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Bugs (GuildID, ReporterID, MessageID, ChannelID, BugDescription, Status) 
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (guild_id, reporter_id, message_id, channel_id, bug_description))
        bug_id = cursor.lastrowid  # Get the last inserted row ID
        conn.commit()
        conn.close()
        return bug_id


    # Method to update the status of a bug report
    def update_bug_status(self, bug_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Bugs
            SET Status = ?
            WHERE BugID = ?
        ''', (status, bug_id))
        conn.commit()
        conn.close()

    # Method to get a bug report by ID
    def get_bug_by_id(self, bug_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Bugs WHERE BugID = ?', (bug_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            columns = ["BugID", "GuildID", "ReporterID", "MessageID", "ChannelID", "BugDescription", "Status"]
            return dict(zip(columns, result))
        return None
    
    def get_bug_by_message_id(self, message_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Bugs WHERE MessageID = ?', (message_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            columns = ["BugID", "GuildID", "ReporterID", "MessageID", "ChannelID", "BugDescription", "Status"]
            return dict(zip(columns, result))
        return None
    
    
    def update_bug(self, bug_id, status, new_channel_id, new_message_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update the status, new channel ID, and new message ID
        cursor.execute('''
            UPDATE Bugs
            SET Status = ?, ChannelID = ?, MessageID = ?
            WHERE BugID = ?
        ''', (status, new_channel_id, new_message_id, bug_id))

        conn.commit()
        conn.close()


    def get_all_bugs(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Bugs')
        results = cursor.fetchall()
        conn.close()

        bugs = []
        if results:
            columns = ["BugID", "GuildID", "ReporterID", "MessageID", "ChannelID", "BugDescription", "Status"]
            for result in results:
                bugs.append(dict(zip(columns, result)))
        return bugs
    
    
    def delete_bug(self, bug_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SQL query to delete the bug report
        cursor.execute('DELETE FROM Bugs WHERE BugID = ?', (bug_id,))

        conn.commit()
        conn.close()
        
        
    def add_application(self, guild_id, app_name, user_id, channel_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Applications (GuildID, AppName, UserID, ChannelID) 
            VALUES (?, ?, ?, ?)
        ''', (guild_id, app_name, user_id, channel_id))
        conn.commit()
        conn.close()

    # Method to get application by ID
    def get_application_by_id(self, application_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Applications WHERE ApplicationID = ?', (application_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            columns = ["ApplicationID", "GuildID", "AppName", "UserID", "ChannelID"]
            return dict(zip(columns, result))
        return None

    # Method to delete an application
    def get_application_by_channel_id(self, channel_id):
        """Retrieve an application record based on the channel ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Applications WHERE ChannelID = ?", (channel_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            columns = ["ApplicationID", "GuildID", "AppName", "UserID", "ChannelID"]
            return dict(zip(columns, result))
        return None

    def delete_application(self, application_id):
        """Delete an application record from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Applications WHERE ApplicationID = ?", (application_id,))
        conn.commit()
        conn.close()

    # Method to get all applications for a guild
    def get_applications_for_guild(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Applications WHERE GuildID = ?', (guild_id,))
        results = cursor.fetchall()
        conn.close()
        applications = []
        for result in results:
            columns = ["ApplicationID", "GuildID", "AppName", "UserID", "ChannelID"]
            applications.append(dict(zip(columns, result)))
        return applications
        
        
        
    def log_application_review_message(self, guild_id, channel_id, message_id, application_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ApplicationReviewMessages (GuildID, ChannelID, MessageID, ApplicationID)
            VALUES (?, ?, ?, ?)
        ''', (guild_id, channel_id, message_id, application_id))
        conn.commit()
        conn.close()

    # Method to retrieve all application review messages
    def get_application_review_messages(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT GuildID, ChannelID, MessageID, ApplicationID FROM ApplicationReviewMessages')
        messages = cursor.fetchall()
        conn.close()
        return messages
    

    def delete_application_review_message(self, channel_id):
        """Delete an application review message record based on the channel ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ApplicationReviewMessages WHERE ChannelID = ?', (channel_id,))
        conn.commit()
        conn.close()