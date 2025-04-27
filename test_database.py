import unittest
import os
import sqlite3
from database import Database

class TestDatabase(unittest.TestCase):
    """Test cases for the database functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Use test database file
        self.test_db_file = "test_hanoi_game.db"
        
        # Remove existing test database if it exists
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
            
        # Create connection and database object
        self.conn = sqlite3.connect(self.test_db_file)
        self.conn.row_factory = sqlite3.Row
        
        # Monkey patch the database file name
        self._original_init = Database.__init__
        Database.__init__ = lambda self: None
        
        self.db = Database()
        self.db.conn = self.conn
        self.db.create_tables()
        
    def tearDown(self):
        """Clean up after tests"""
        self.conn.close()
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
        
        # Restore original init method
        Database.__init__ = self._original_init
        
    def test_create_tables(self):
        """Test that tables are created correctly"""
        # Check users table
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check games table
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check algorithm_performance table
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='algorithm_performance'")
        self.assertIsNotNone(cursor.fetchone())
        
    def test_get_or_create_user(self):
        """Test user creation and retrieval"""
        # Create new user
        user_id1 = self.db.get_or_create_user("TestUser1")
        self.assertIsNotNone(user_id1)
        
        # Get existing user
        user_id2 = self.db.get_or_create_user("TestUser1")
        self.assertEqual(user_id1, user_id2)
        
        # Create another user
        user_id3 = self.db.get_or_create_user("TestUser2")
        self.assertNotEqual(user_id1, user_id3)
        
    def test_save_result(self):
        """Test saving game results"""
        # Prepare test data
        name = "TestPlayer"
        disks = 3
        pegs = 4
        completed = True
        times = {
            'recursive': 0.001,
            'iterative': 0.002,
            'frame_stewart': 0.0015
        }
        user_time = 30
        user_moves = "A->B,A->C,B->C"
        is_correct = True
        efficiency_note = "4-peg solution is more efficient"
        
        # Save result
        result = self.db.save_result(
            name, disks, pegs, completed, times, 
            user_time, user_moves, is_correct, efficiency_note
        )
        self.assertTrue(result)
        
        # Check game was saved
        cursor = self.conn.execute("SELECT * FROM games")
        game = cursor.fetchone()
        self.assertIsNotNone(game)
        self.assertEqual(game['disks'], disks)
        self.assertEqual(game['pegs'], pegs)
        self.assertEqual(game['user_time'], user_time)
        self.assertEqual(game['user_moves'], user_moves)
        self.assertEqual(game['is_correct'], is_correct)
        self.assertEqual(game['efficiency_note'], efficiency_note)
        
        # Check algorithm performance was saved
        cursor = self.conn.execute("SELECT * FROM algorithm_performance")
        performances = cursor.fetchall()
        self.assertEqual(len(performances), 3)  # Three algorithms
        
    def test_get_top_scores(self):
        """Test retrieving top scores"""
        # Add test users
        user1_id = self.db.get_or_create_user("Player1")
        user2_id = self.db.get_or_create_user("Player2")
        
        # Add test games
        self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time) VALUES (?, ?, ?, ?, ?)",
            (user1_id, 3, 3, 1, 50)
        )
        self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time) VALUES (?, ?, ?, ?, ?)",
            (user2_id, 4, 3, 1, 30)
        )
        self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time) VALUES (?, ?, ?, ?, ?)",
            (user1_id, 5, 4, 1, 40)
        )
        self.conn.commit()
        
        # Get top scores
        top_scores = self.db.get_top_scores(2)
        
        # Verify results
        self.assertEqual(len(top_scores), 2)
        self.assertEqual(top_scores[0]['user_time'], 30)  # Fastest time first
        self.assertEqual(top_scores[1]['user_time'], 40)  # Second fastest
        
    def test_get_algorithm_stats(self):
        """Test retrieving algorithm stats"""
        # Create a test game
        game_id = self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time) VALUES (?, ?, ?, ?, ?)",
            (1, 3, 3, 1, 50)
        ).lastrowid
        
        # Add algorithm performance data
        self.conn.execute(
            "INSERT INTO algorithm_performance (game_id, algorithm_name, execution_time) VALUES (?, ?, ?)",
            (game_id, 'recursive', 0.001)
        )
        self.conn.execute(
            "INSERT INTO algorithm_performance (game_id, algorithm_name, execution_time) VALUES (?, ?, ?)",
            (game_id, 'recursive', 0.003)
        )
        self.conn.execute(
            "INSERT INTO algorithm_performance (game_id, algorithm_name, execution_time) VALUES (?, ?, ?)",
            (game_id, 'iterative', 0.002)
        )
        self.conn.commit()
        
        # Get stats
        stats = self.db.get_algorithm_stats()
        
        # Verify results
        self.assertIn('recursive', stats)
        self.assertIn('iterative', stats)
        self.assertEqual(stats['recursive'], 0.002)  # Average of 0.001 and 0.003
        self.assertEqual(stats['iterative'], 0.002)
        
    def test_get_user_stats(self):
        """Test retrieving user statistics"""
        # Create test user
        username = "StatsTestUser"
        user_id = self.db.get_or_create_user(username)
        
        # Add test games
        self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time, is_correct) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, 3, 3, 1, 50, 1)
        )
        self.conn.execute(
            "INSERT INTO games (user_id, disks, pegs, completed, user_time, is_correct) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, 4, 3, 1, 30, 0)
        )
        self.conn.commit()
        
        # Get user stats
        stats = self.db.get_user_stats(username)
        
        # Verify results
        self.assertIsNotNone(stats)
        self.assertEqual(stats['games_played'], 2)
        self.assertEqual(stats['avg_time'], 40)  # Average of 50 and 30
        self.assertEqual(stats['best_time'], 30)
        self.assertEqual(stats['correct_predictions'], 1)  # Only one correct prediction


if __name__ == '__main__':
    unittest.main()