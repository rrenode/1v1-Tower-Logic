from datbasemanager import DatabaseManager

class CalloutManager:
    def __init__(self, last_rankings_pos=20):
        self.rankings_cutoff = last_rankings_pos

        self.db_manager = DatabaseManager()
    
    def reset_player_list(self, player_csv=None):
        if player_csv:
            i = 1
            for row in player_csv:
                self.db_manager.add_player(
                    did = row[0],
                    username = row[1],
                    standing = i
                )
                i += 1
            return
        else:
            print("Please provide a csv file with two columns, discord id's and usernames. The csv should be in order of the leaderboard.")
    
    def close(self):
        self.db_manager.close()
    
    @property
    def player_standings(self):
        return self.db_manager.player_standings