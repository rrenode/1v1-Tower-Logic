from unittest.mock import MagicMock
import unittest

from datetime import datetime, timedelta

import discord
from main import Bot
from callout import CalloutManager

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.bot = Bot()
        self.cm = CalloutManager()
        self.bot.cm = self.cm
        
        # Mock database manager
        self.cm.db_manager = MagicMock()

        # Create some mock users
        self.rubben = discord.Member("1", "Rubben")
        self.dunion = discord.Member("2", "Dunion")
        self.loupy = discord.Member("3", "Loupy")
        
        # Setup default mock responses for database manager methods
        self.cm.db_manager.get_player_standing.side_effect = lambda did, with_position=True: {
            "1": 1,
            "2": 2,
            "3": 3
        }.get(did, 99)
        
        self.cm.db_manager.get_player_username.side_effect = lambda did: {
            "1": "Rubben",
            "2": "Dunion",
            "3": "Loupy"
        }.get(did, "Unknown")
        
        self.cm.db_manager.add_callout.return_value = ("callout_id", datetime.now() + timedelta(days=1))
        self.cm.db_manager.get_did_at_standing.side_effect = lambda pos: {
            1: "1",
            2: "2",
            3: "3"
        }.get(pos, "Unknown")
    def test_callout_challenge(self):
        # Simulate no active callouts for the challenger
        self.cm.db_manager.get_callouts_by_challenger.return_value = []
        self.cm.db_manager.get_callouts_by_standing.return_value = []
        
        self.bot.callout(self.dunion)
        
        # Verify that add_callout was called with expected arguments
        self.cm.db_manager.add_callout.assert_called_once_with(
            challenger="2",
            for_position_num=1,
            waiting_on=None,
            callout_standing="Rankings",
            status="Pending Response"
        )

    def test_accept_callout(self):
        # Simulate a pending callout for the user to accept
        self.cm.db_manager.get_callouts_by_standing.return_value = [
            MagicMock(id="callout_id", challenger="2", for_position_num=1, status="Pending Response")
        ]
        
        self.bot.accept_callout(self.rubben)
        
        # Verify that update_callout_status was called with expected arguments
        self.cm.db_manager.update_callout_status.assert_called_once_with("callout_id", "Accepted")
        
        # Verify that update_callout_expiration was called once
        self.cm.db_manager.update_callout_expiration.assert_called_once_with("callout_id")

    def test_report_win(self):
        # Simulate an accepted callout for the challenger
        self.cm.db_manager.get_callouts_by_challenger.return_value = [
            MagicMock(id="callout_id", challenger="2", for_position_num=1, status="Accepted")
        ]
        
        self.bot.report(self.dunion, "win")
        
        # Verify that update_callout_status was called with expected arguments
        self.cm.db_manager.update_callout_status.assert_called_with("callout_id", "Challenger win")
        
        # Verify that swap_player_standing was called
        self.cm.db_manager.swap_player_standing.assert_called_once()

    def test_report_invalid_result(self):
        # Simulate an accepted callout for the challenger
        self.cm.db_manager.get_callouts_by_challenger.return_value = [
            MagicMock(id="callout_id", challenger="2", for_position_num=1, status="Accepted")
        ]
        
        with self.assertRaises(ValueError):  # Expecting an exception due to invalid result
            self.bot.report(self.dunion, "invalid_result")
        
        # Verify no calls were made to update_callout_status or swap_player_standing
        self.cm.db_manager.update_callout_status.assert_not_called()
        self.cm.db_manager.swap_player_standing.assert_not_called()

    def test_callout_self_challenge(self):
        # Simulate the challenger's standing
        self.cm.db_manager.get_player_standing.return_value = 2
        
        with self.assertRaises(ValueError):  # Expecting an exception due to silly self-challenge
            self.bot.callout(self.dunion, self.dunion)
        
        # Verify add_callout was not called
        self.cm.db_manager.add_callout.assert_not_called()

if __name__ == '__main__':
    unittest.main()