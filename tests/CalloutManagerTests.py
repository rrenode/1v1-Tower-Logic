from unittest.mock import MagicMock
import unittest

from callout import CalloutManager

class TestCalloutManager(unittest.TestCase):

    def setUp(self):
        # Initialize CalloutManager
        self.cm = CalloutManager()
        
        # Mock the DatabaseManager
        self.cm.db_manager = MagicMock()

        # Example CSV data (discord_id, username)
        self.player_csv = [
            ["12345", "player1"],
            ["67890", "player2"],
            ["54321", "player3"]
        ]

    def test_reset_player_list(self):
        # Call the method under test
        self.cm.reset_player_list(self.player_csv)

        # Verify that add_player was called with expected arguments
        expected_calls = [
            (("12345", "player1", 1),),
            (("67890", "player2", 2),),
            (("54321", "player3", 3),)
        ]
        actual_calls = [call.args for call in self.cm.db_manager.add_player.call_args_list]

        self.assertEqual(expected_calls, actual_calls)
    
    def test_reset_player_list_no_csv(self):
        with self.assertLogs(level='INFO') as log:
            self.cm.reset_player_list()
            self.assertIn("Please provide a csv file with two columns, discord id's and usernames. The csv should be in order of the leaderboard.", log.output[0])

    def test_player_standings(self):
        # Setup the mock return value
        self.cm.db_manager.player_standings = "Expected Standings"

        # Verify the property returns the expected value
        self.assertEqual(self.cm.player_standings, "Expected Standings")

if __name__ == '__main__':
    unittest.main()