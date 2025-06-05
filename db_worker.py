from sqlite3 import Connection
from time import time



class database:
    def __init__(self) -> None:
        self.connect = Connection("db.db", isolation_level=None, check_same_thread=False)
        
    
    def get_user_info(self, id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("SELECT * FROM users WHERE id=?", (id,))
            data = cursor.fetchone()
            if data is None:
                data = (id, None, True)
                cursor.execute("INSERT INTO users VALUES(?,?,?)", data)
            return data


    def new_log(self, user_info: dict):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("SELECT * FROM logs WHERE id=?", (user_info['id'],))
            data = cursor.fetchall()
            new_data = (user_info['id'],
                user_info['username'],
                user_info['photo_url'],
                user_info['ip'],
                user_info['port'],
                user_info['user_agent'],
                user_info['creator'])
            is_similar = False
            for log in data:
                if tuple(log) == new_data:
                    is_similar = True
            if not is_similar:
                cursor.execute("INSERT INTO logs VALUES(?,?,?,?,?,?,?)", new_data)
                return True
            return False
    

    def add_subscription(self, id: int, duration: float):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("UPDATE users SET subscription=? WHERE id=?", (time() + duration, id))
    

    def remove_subscription(self, id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("UPDATE users SET subscription=? WHERE id=?", (None, id))
            
    
    def get_logs_by_creator(self, creator_id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("SELECT * FROM logs WHERE log_owner=?", (creator_id,))
            return cursor.fetchall()
    
    def get_logs_by_id(self, id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("SELECT * FROM logs WHERE id=?", (id,))
            return cursor.fetchall()
        
    def get_logs_by_username(self, username: str):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("SELECT * FROM logs WHERE username=?", (username,))
            return cursor.fetchall()
        
    def set_notifications_true(self, id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("UPDATE users SET notifications=? WHERE id=?", (True, id))
            return cursor.fetchall()

    def set_notifications_false(self, id: int):
        with self.connect:
            cursor = self.connect.cursor()
            cursor.execute("UPDATE users SET notifications=? WHERE id=?", (False, id))
            return cursor.fetchall()