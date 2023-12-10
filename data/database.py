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