from datetime import datetime, timedelta
import csv

from callout import CalloutManager

cm = CalloutManager()

def get_players_csv():
    player_list_file = "thelist.csv"
    rows = []
    # reading csv file
    with open(player_list_file, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)
        rows.pop(0)
    return rows

def refresh_database():
    rows = get_players_csv()
    cm.reset_player_list(rows)

class DiscordUser:
    # Simulates if the logic was integrated as a discord bot
    def __init__(self, id, username):
        self.id = id
        self.username = username

class Bot:
    def __init__(self):
        self.admin_role_id = 1245466547

    def format_timedelta(self, td):
        days = td.days
        seconds = td.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

    def callout(self, ctx_user : DiscordUser, challengee : DiscordUser = None, **kargs):
        match_type = None
        challengee_position = None
        challenger_position = cm.db_manager.get_player_standing(ctx_user.id, True)
        challenger_callouts = cm.db_manager.get_callouts_by_challenger(did=ctx_user.id)
        # Players cannot callout someone else if they are the challenger in another callout
        if challenger_callouts:
            # Discord error message
            print("You already have an active callout on someone.")
            return
        # Challenger is in The List and tried to specify who they're challenging
        if challengee and challenger_position < 21:
            # Discord error message
            print("You cannot specify who you're challenging when in The List. Must challenge for the spot about you.")
            return
        # Promotion game from waitlist to The List
        elif challenger_position == 21:
            match_type = "Promotion"
            if challengee:
                # Discord error message
                print("You cannot specify who you're challenging when in the top of the Wait List. Must challenge the spot about you.")
                return
            challengee_position = 20            
        elif not challengee or challenger_position < 21:
            match_type = "Rankings"
            # Challenger in waitlist tries to challenge someone in The List
            if challenger_position > 20:
                # Discord error message
                print("Error: Except when at the top, players must designate who their challenger is when in the waitlist.")
                return
            # The challenger in position 1 of The List must routinely challenge the last player in The List
            if challenger_position == 1:
                challengee_position = 20
            else:
                challengee_position = challenger_position - 1
        # Waitlist Challenges
        else:
            match_type = "Waitlist" 
            challengee_position = cm.db_manager.get_player_standing(challengee.id, True)
            pos_difference = challenger_position - challengee_position
            # Waitlist players cannot challenge players in The List, unless they themselves are at the top of the waitlist
            if challengee_position < 21 and challenger_position != 21:
                # Discord error message
                print("Cannout challenge someone in The List while you are in the Wait List and not at the top.")
                return
            # Players can only challenge someone who is within five spots of them
            if pos_difference == 0:
                # Discord error message
                print("Cannot challenge yourself. Nice try ;)")
                return
            if pos_difference < 0:
                # Discord error message
                print("You must challenge a player above you, not below.")
                return
            if pos_difference > 5:
                # Discord error message
                print("You are attempting to challenge someone that is not within 5 spots from you.")
                return
        
        # Players can only challenge someone who isn't part of an active callout [Scenario 4]
        challengee_did = cm.db_manager.get_did_at_standing(challengee_position)
        challengee_standing = cm.db_manager.get_player_standing(challengee_did)
        excluded_statuses = ("'Challenger win'", "'Challenger Loss'", "'Forfeit by decline'", "'Forfeit by timeout'")
        status_condition = f"AND status NOT IN ({', '.join(excluded_statuses)})"
        callouts = cm.db_manager.get_callouts_by_standing(challengee_standing, status_condition, callout_standing="Waitlist")
        if callouts:
            # Discord error message
            print("The player you're attempting to challenge already has an active callout.")
            return

        challenger = cm.db_manager.get_player(ctx_user.id)
        challengee_username = cm.db_manager.get_player_username(challengee_did)
        if challenger.challengee_loss_time:
            last_lost_time = datetime.fromisoformat(challenger.challengee_loss_time)
            last_lost_to = challenger.challengee_lost_to
            time_remaining = (last_lost_time + timedelta(hours=24)) - datetime.now()
            if datetime.now() > last_lost_time and last_lost_to == challengee_did:
                # Discord error message
                print(f"You cannot challenge {challengee_username} until you are either challenged by someone below you or 24-hours elapses from your loss to them.")
                print(f"Current time left: {self.format_timedelta(time_remaining)}")
                return
        try:
            callout = cm.db_manager.add_callout(
                challenger=ctx_user.id, 
                for_position_num=challengee_position, 
                waiting_on=None, 
                callout_standing=match_type, 
                status="Pending Response"
            )
        except Exception as e:
            # Discord error message
            print(f"Failed to create a callout: \n {e}")
            return
        
        if callout:
            challenger_username = ctx_user.username
            challengee_did = cm.db_manager.get_did_at_standing(challengee_position)
            challengee_username = cm.db_manager.get_player_username(challengee_did)
            expiration_date = callout[1]

            # In an embed in a channel that shows callouts, or just in the tower bot channel
            print(f"{challenger_username} called out position {challengee_position}!")
            print(f"\tCurrent Position Holder: {challengee_username}")
            print(f"\tChallengee Must respond by: {expiration_date}")
    
    def dm_new_callout(self, challengee_name, callout_id):
        callout_data = cm.db_manager.get_callout_by_id(callout_id)
        # In an embed
        print(f"Hey @{challengee_name}, {callout_data.challenger} has called you the f@%k out!")
        print(f"Either click the accept or decline buttons below OR you can type `/accept_callout` or `/decline_callout` in #TheList-Bot-Commands.")
        return

    def accept_callout(self, ctx_user):
        # User needs to have an active callout
        ctx_user_pos = cm.db_manager.get_player_standing(ctx_user.id)
        callouts = cm.db_manager.get_callouts_by_standing(ctx_user_pos, status = "Pending Response")
        callout = None
        if not callouts:
            # Discord error message
            print("You have no callouts awaiting your response.")
            return
        if len(callouts) > 1:
            # Discord error message
            print("Fatal error: Multiple active callouts registered to your user id. Please contact a moderator.")
            return
        else:
            callout = callouts[0]
        cm.db_manager.update_callout_expiration(callout.id)
        cm.db_manager.update_callout_status(callout.id,"Accepted")
        challenger_username = cm.db_manager.get_player_username(callout.challenger)
        # Discord message
        print(f"You have accepted the callout from {challenger_username}.")
    
    def decline_callout(self, ctx_user):
        # User needs to have an active callout
        ctx_user_pos = cm.db_manager.get_did_at_standing(ctx_user.id)
        callouts = cm.db_manager.get_callouts_by_standing(ctx_user_pos, status = "Pending Response")
        callout = None
        if not callouts:
            # Discord error message
            print("You have no callouts awaiting your response.")
            return
        if len(callouts) > 1:
            # Discord error message
            print("Fatal error: Multiple active callouts registered to your user id. Please contact a moderator.")
            return
        else:
            callout = callouts[0]
        new_position = callout.for_position_num
        cm.db_manager.update_player_last_loss(ctx_user.id, callout.challenger)
        cm.db_manager.swap_player_standing(ctx_user.id,callout.challenger)
        challenger_username = cm.db_manager.get_player_username(callout.challenger)
        cm.db_manager.update_callout_status(callout.id,"Forfeit by decline")
        # Discord message
        print(f"You have declined the callout from {challenger_username}. This counts as a forfeit. You are now position {new_position}")

    def report(self, ctx_user, result : str):
        accepted_callouts = cm.db_manager.get_callouts_by_challenger(ctx_user.id, status = "Accepted")
        pending_callouts = cm.db_manager.get_callouts_by_challenger(ctx_user.id, status = "Pending Response")
        callouts = accepted_callouts + pending_callouts
        callout = None
        if not callouts:
            # Discord error message
            print("You have not called someone out. Note: Only challengers can report win or losses.")
            return
        if pending_callouts:
            # Discord error message
            print("You have an active callout on a player and are still awaiting their response.")
            return
        if len(pending_callouts) > 1:
            # Discord error message
            print("Fatal error: Multiple active callouts registered to your user id. Please contact a moderator.")
            return
        else:
            callout = callouts[0]
        win_results = ["win", "w", "dub"]
        loss_results = ["loss", "l"]
        all_possible_results = win_results + loss_results
        formatted_options = ', '.join(f'`{option}`' for option in all_possible_results)
        if result.lower() not in all_possible_results:
            # Discord error message
            print(f"Invalid result. Possible options are: {formatted_options}. Capitalization does not matter.")
            return
        if result.lower() in win_results:
            challengee_did = cm.db_manager.get_did_at_standing(callout.for_position_num)
            cm.db_manager.update_callout_status(callout.id,"Challenger win")
            if cm.db_manager.get_player_standing(ctx_user.id) == 1 and callout.callout_standing == "Rankings":
                # Discord message
                print("Nice win. Remmber that the number 1 spot must periodically challenge the number 20 spot in the rankings.")
                return
            cm.db_manager.swap_player_standing(ctx_user.id,challengee_did)
            cm.db_manager.update_player_last_loss(challengee_did, ctx_user.id)
            #cm.db_manager.update_player_last_loss(ctx_user.id, None)
            new_position = callout.for_position_num
            if new_position == 20:
                cm.db_manager.delete_player(challengee_did)
                # Discord message
                print("Congrdulations on the promotion and welcome to The List!")
            # Discord message
            print(f"Nice. You are now in position: {new_position}")
        elif result.lower() in loss_results:
            cm.db_manager.update_player_last_loss(challengee_did, None)
            cm.db_manager.update_player_last_loss(ctx_user.id, challengee_did)
            cm.db_manager.update_callout_status(callout.id,"Challenger loss")
            # Discord message
            print("Server presses `f` to pay respects....... NOT")
    
    # Admin/Moderator Commands
    def reset_db(self, csv_file):
        pass


bot = Bot()

refresh_database()
rows = get_players_csv()

rubben =    DiscordUser(rows[0][0],  rows[0][1])
dunion =    DiscordUser(rows[1][0],  rows[1][1])
loupy =     DiscordUser(rows[2][0],  rows[2][1])
fish_taco = DiscordUser(rows[3][0], rows[3][1])
herrobear = DiscordUser(rows[19][0], rows[19][1])
rob =       DiscordUser(rows[20][0], rows[20][1])
fyshi =     DiscordUser(rows[23][0], rows[23][1])
kingpin =   DiscordUser(rows[25][0], rows[25][1])
flykid =    DiscordUser(rows[27][0], rows[27][1])
trainee =   DiscordUser(rows[30][0], rows[30][1])

# ==========================================
#                  Questions
# ==========================================
#   - RESOLVED: Strain is on the challengee aka, if no game, regardless of anything, then challenger takes challengee's spot; 
# though the challengee may contest the ruling if, and only if, the challenger put, in the opinion of the moderator, 
# too little effort into scheduling a match. Challengee can report in thread if there is scheduling problems on the challenger's 
# end but must do so 6 hours prior to the 48 hour rule ending.
# || What happens when the 72 hour (now 48 hour) rule elapses and no game has been played?
#   - Is the strain on the challenger or the challengee? OR
#   - Is it context dependant? If so, should I add functionality to ping a 1v1s tower mod for them to make a decision?.
#
#   - RESOLVED: Make threads. Only the two players that are a part of the callout can use text chat in the thread; this would 
# have to be done through the bot as permissions are applied accross all posts in a form. Bot states in thread: "Make sure all
# communication regarding the callout remains in the thread."
# || I can make it so that when someone calls someone out, a new thread is automatically created that only the
# challenger and the challenged (as well as mods) can message in. We can then restrict the rest of the commands to only 
# work in the callout threads. The benefits are two fold, organization assiting with moderation and programming the bot
# becomes easier because then I can simply assign the new thread id to the callout id.
#
#   - RESOLVED: Players can only have one callout active on them
# || Speaking of which, currently callouts are handled in that players can only have one active callout that they made 
# and only have one active callout from others. Is a queue system prefered or do you prefer that people wait for the 
# callout to finish and those who wanted to challenge that player just try to callout that guy first?
#
#   - RESOLVED: 48 hour rule covers this.
# || Scenario 2 can't really be enforced through a bot unless we also make players use a command to schedule their game.
# With that then comes, how are they punished. So, I personally say that this scenario is pointless to code other than.
#
# - Players are expected to challenge up, inform them
#
# - Players can only go down 1 spot every 2 days, if they are on vacation
#
# - Players can "go on vacation", they can take a maximum of two weeks of vacation time per year.
# - Players input amount of time in days.
# - Creates a vacation thread, informs tower moderator. Moderator approves or declines.
# - Time is based only in days. Even when you leave vacation mode early, you are charged for the amount of days every 24 hours; vacation starts at midnight;
# they can put what they their vacation starts. Bot counts each day from midnight, even if they return a minute after midnight, it is a day.
# - If someone who's called out is on vacation, then the bot automatically accepts the callout. Then the 48 hour timer runs as normal.
# - Player's on vacation can't run commands until they run the command to leave vacation mode.
# - Moderation command to start vacation mode for a player or to allot more vacation time
#
# - New players can do /join and they go to the last spot in the waitlist
#
# - Inform players when their calledout position has changed hands
# 
# - Waitlist players can just type /callout. Creates an embed with the possible players they can callout. Players within the
# 5 spots of the challenger who already have an active callout on them are greyed out.
#
# Inform players if the player they are challenging has active callouts; button is yellow. Green if no active callout.
# In Embed:
# Username  | Position
# Player1   |    34
# Player2   |    33
#
# In the button:
# Playername (POS. 23)

# ==========================================
#                   Tests
# ==========================================
# Number 2 spot challenges the number 1 spot
"""
bot.callout(dunion) # Pos_2 calls out Pos_1 || Callout created
bot.accept_callout(rubben) # Pos_1 accepts || Nice
bot.report(dunion, "win")
"""

# Promotion game from waitlist into the rankings
"""
bot.callout(rob)
bot.accept_callout(herrobear)
bot.report(rob, "win")
"""

# [Scenario 1 & 3] Player loses to challenger, goes down, and can't challenge for 24 hours
# or until another challenges them. Scenarios 1 and 3 are the same scenario, 3 only being an extension.

# In Rankings
"""
bot.callout(loupy)
bot.accept_callout(dunion)
bot.report(loupy, "win")
bot.callout(dunion) # || Silly user
bot.callout(fish_taco)
bot.callout(dunion) # || Silly user
bot.accept_callout(dunion)
bot.report(fish_taco, "loss")
bot.callout(dunion) # || User figured it out
"""

# In Waitlist
"""
bot.callout(trainee, flykid)
bot.accept_callout(flykid)
bot.report(trainee, "win")
bot.callout(flykid, trainee) # || Silly user
"""

# [Scenario 4] player on the waitlist already has an active callout on them, a second player 
# may not call them out until that match has been played. AKA: Players, regardless of ranking, can have one 
# active callout on them and one active callout placed on others 

"""
bot.callout(kingpin, fyshi)
bot.callout(flykid, fyshi)
bot.accept_callout(fyshi)
bot.report(kingpin, 'w')
bot.callout(flykid, fyshi)
"""

# [Extras]

# Making sure the logic catches user error
"""
bot.callout(fyshi, dunion) # Pos_24 (waitlist) calls out Pos_2 || Silly user
bot.callout(fyshi, herrobear) # Pos_24 (waitlist) calls out Pos_20 || Silly user
bot.callout(trainee, fyshi) # Pos_31 calls out Pos_22 || Silly user
"""