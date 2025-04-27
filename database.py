import sqlite3
import os.path

class Database:
    def __init__(self):
        db_exists = os.path.exists("hanoi_game.db")
        self.conn = sqlite3.connect("hanoi_game.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        if not db_exists:
            self.create_tables()
        else:
            self.migrate_schema()

    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                disks INTEGER NOT NULL,
                pegs INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                user_time INTEGER,
                user_moves TEXT,
                actual_moves TEXT,
                is_correct BOOLEAN,
                efficiency_note TEXT,
                min_moves INTEGER,  # Added column for minimum moves
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS algorithm_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                algorithm_name TEXT NOT NULL,
                execution_time REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')

        self.conn.commit()

    def migrate_schema(self):
        try:
            cursor = self.conn.execute("PRAGMA table_info(games)")
            columns = [row['name'] for row in cursor.fetchall()]
            
            if 'actual_moves' not in columns:
                self.conn.execute("ALTER TABLE games ADD COLUMN actual_moves TEXT")
                self.conn.commit()
                
            if 'min_moves' not in columns:
                self.conn.execute("ALTER TABLE games ADD COLUMN min_moves INTEGER")
                self.conn.commit()
                
        except Exception as e:
            print(f"Migration error: {e}")

    def get_or_create_user(self, username):
        cursor = self.conn.execute("SELECT id FROM users WHERE name = ?", (username,))
        user = cursor.fetchone()

        if user:
            return user['id']
        else:
            cursor = self.conn.execute("INSERT INTO users (name) VALUES (?)", (username,))
            self.conn.commit()
            return cursor.lastrowid

    def save_result(self, name, disks, pegs, completed, times, user_time, user_moves, is_correct, efficiency_note="", actual_moves="", min_moves=None):
        try:
            user_id = self.get_or_create_user(name)
            cursor = self.conn.execute('''
                INSERT INTO games (
                    user_id, disks, pegs, completed,
                    user_time, user_moves, actual_moves,
                    is_correct, efficiency_note, min_moves
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, disks, pegs, completed,
                user_time, user_moves, actual_moves,
                is_correct, efficiency_note, min_moves
            ))

            game_id = cursor.lastrowid

            for algo, time_value in times.items():
                if time_value is not None:
                    self.conn.execute('''
                        INSERT INTO algorithm_performance (game_id, algorithm_name, execution_time)
                        VALUES (?, ?, ?)
                    ''', (game_id, algo, time_value))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_top_scores(self, limit=10):
        try:
            cursor = self.conn.execute('''
                SELECT u.name, g.user_time, g.disks, g.pegs
                FROM games g
                JOIN users u ON g.user_id = u.id
                WHERE g.completed = 1
                ORDER BY g.user_time ASC
                LIMIT ?
            ''', (limit,))

            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting top scores: {e}")
            return []

    def get_algorithm_stats(self):
        try:
            stats = {}
            algorithms = ['recursive', 'iterative', 'frame_stewart']

            for algo in algorithms:
                cursor = self.conn.execute('''
                    SELECT AVG(execution_time) as avg_time
                    FROM algorithm_performance
                    WHERE algorithm_name = ?
                ''', (algo,))

                result = cursor.fetchone()
                if result and result['avg_time'] is not None:
                    stats[algo] = result['avg_time']

            return stats

        except Exception as e:
            print(f"Error getting algorithm stats: {e}")
            return {}

    def get_user_stats(self, username):
        try:
            user_id = self.get_or_create_user(username)

            cursor = self.conn.execute('''
                SELECT 
                    COUNT(*) as games_played,
                    AVG(user_time) as avg_time,
                    MIN(user_time) as best_time,
                    SUM(is_correct) as correct_predictions
                FROM games
                WHERE user_id = ? AND completed = 1
            ''', (user_id,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None