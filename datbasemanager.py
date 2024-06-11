import sqlite3
from datetime import datetime, timedelta

class Player:
    def __init__(self, id, did, username, standing, challengee_loss_time=None, challengee_lost_to=None):
        self.did = did
        self.username = username
        self.standing = standing
        self.challengee_loss_time = challengee_loss_time
        self.challengee_lost_to = challengee_lost_to
    
    def __str__(self):
        return f"""Discord ID: {self.did}\nUsername: {self.username}\nStanding: {self.standing}"""

class CalloutObject:
    def __init__(self, id, challenger, callout_timestamp, callout_expiration, completion_date, 
                 for_position_num, waiting_on, callout_standing, status):
        self.id = id
        self.challenger = challenger
        self.callout_timestamp = callout_timestamp
        self.callout_expiration = callout_expiration
        self.completion_date = completion_date
        self.for_position_num = for_position_num
        self.waiting_on = waiting_on
        self.callout_standing = callout_standing
        self.status = status

class DatabaseManager:
    def __init__(self, db_name="Storage/db/1v1_tower_1.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_callout_table()
        self.create_leaderboard_table()

    def create_callout_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS callouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger INTEGER NOT NULL,
                callout_timestamp TEXT NOT NULL,
                callout_expiration TEXT NOT NULL,
                completion_date TEXT,
                for_position_num INTEGER NOT NULL,
                waiting_on INTEGER,
                callout_standing TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_callout(self, challenger, for_position_num, waiting_on, callout_standing, status):
        callout_timestamp = datetime.now().isoformat()
        callout_expiration = (datetime.now() + timedelta(hours=24)).isoformat()
        self.cursor.execute("""
            INSERT INTO callouts (challenger, callout_timestamp, callout_expiration, 
                                  for_position_num, waiting_on, callout_standing, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (challenger, callout_timestamp, callout_expiration, for_position_num, waiting_on, callout_standing, status))
        self.conn.commit()
        row_id = self.cursor.lastrowid
        return [callout_timestamp, callout_expiration, row_id]

    def get_all_callouts(self):
        self.cursor.execute("SELECT * FROM callouts")
        rows = self.cursor.fetchall()
        callouts = [CalloutObject(*row) for row in rows]
        return callouts

    def get_callout_by_id(self, id):
        # Aka, get callouts the player activated themselves
        self.cursor.execute("SELECT * FROM callouts WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        if row:
            return CalloutObject(*row)
        return None

    def get_callouts_by_challenger(self, did, **kwargs):
        # Aka, get callout the player activated themselves
        query = "SELECT * FROM callouts WHERE challenger = ?"
        params = [did]
        for key, value in kwargs.items():
            query += f" AND {key} = ?"
            params.append(value)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        if rows:
            return [CalloutObject(*row) for row in rows]
        return []

    def get_callouts_by_standing(self, challengee_pos, *args, **kwargs):
        # Aka, what callouts are for a specified position
        query = "SELECT * FROM callouts WHERE for_position_num = ?"
        params = [challengee_pos]
        for value in args:
            query += str(value)
        for key, value in kwargs.items():
            query += f" AND {key} = ?"
            params.append(value)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        if rows:
            return [CalloutObject(*row) for row in rows]
        return []

    def update_callout_status(self, id, new_status):
        self.cursor.execute("UPDATE callouts SET status = ? WHERE id = ?", (new_status, id))
        self.conn.commit()
    
    def update_callout_expiration(self, id):
        callout = self.get_callout_by_id(id)
        callout_creation = datetime.fromisoformat(callout.callout_timestamp)
        expiration_time = (callout_creation + timedelta(hours=72)).isoformat()
        self.cursor.execute("UPDATE callouts SET callout_expiration = ? WHERE id = ?", (expiration_time, id))
        self.conn.commit()

    def delete_callout(self, id):
        self.cursor.execute("DELETE FROM callouts WHERE id = ?", (id,))
        self.conn.commit()

    def create_leaderboard_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                did INTEGER NOT NULL,
                username TEXT NOT NULL,
                standing INTEGER NOT NULL,
                challengee_loss_time TEXT,
                challengee_lost_to INTEGER
            )
        """)
        self.conn.commit()
    
    def add_player(self, did, username, standing):
        self.cursor.execute("""
            INSERT INTO leaderboard (did, username, standing)
            VALUES (?, ?, ?)
        """, (did, username, standing))
        self.conn.commit()
    
    def get_player_username(self, did):
        self.cursor.execute("SELECT username FROM leaderboard WHERE did = ?", (did,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
    
    def get_player_standing(self, player_did, as_int = False):
        self.cursor.execute("SELECT standing FROM leaderboard WHERE did = ?", (player_did,))
        row = self.cursor.fetchone()
        if as_int:
            return int(row[0])
        return row[0]
    
    def get_did_at_standing(self, standing):
        self.cursor.execute("SELECT did FROM leaderboard WHERE standing = ?", (standing,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
    
    def get_player(self, did):
        self.cursor.execute("SELECT * FROM leaderboard WHERE did = ?", (did,))
        row = self.cursor.fetchone()
        return Player(*row)

    def update_player_last_loss(self, did, last_lost_to):
        challengee_loss_time = None
        if last_lost_to == None:
            query = "UPDATE leaderboard set challengee_loss_time = ?, challengee_lost_to = ? WHERE did = ?"
            last_lost_to = None
        else:
            query = "UPDATE leaderboard set challengee_loss_time = ?, challengee_lost_to = ? WHERE did = ?"
            challengee_loss_time = datetime.now().isoformat()
        self.cursor.execute(
            query, 
            (challengee_loss_time, last_lost_to, did)
                        )
        self.conn.commit()

    def swap_player_standing(self, player1_did, player2_did):
        player1_standing = self.get_player_standing(player1_did)
        player2_standing = self.get_player_standing(player2_did)

        if player1_standing and player2_standing:
            # Swap standings
            self.cursor.execute("UPDATE leaderboard SET standing = ? WHERE did = ?", (player2_standing, player1_did))
            self.cursor.execute("UPDATE leaderboard SET standing = ? WHERE did = ?", (player1_standing, player2_did))
            self.conn.commit()
    
    def delete_player(self, did):
        self.cursor.execute("DELETE FROM leaderboard WHERE did = ?", (did,))
        self.conn.commit()

    def close(self):
        self.conn.close()
    
    @property
    def player_standings(self):
        self.cursor.execute("SELECT * FROM leaderboard")
        rows = self.cursor.fetchall()
        standings = [Player(*row) for row in rows]
        return standings