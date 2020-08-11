
"""Pro-Trader is program that will determine if a proposed NFL trade involving any two skill players will be benificial to your team"""

from bs4 import BeautifulSoup
import requests
import sys
import bs4

"""Parent class"""
class Player:

    def __init__(self, gamesPlayed):
        self.games = gamesPlayed

    """Method that will adjust statistics if a player does not play a full season
    as if the player participated in a full 16 game season, Statistics will not
    be adjusted if the player did no participate in less than 8 games"""
    def appropriate(self, gamesPlayed, stat):


        if gamesPlayed == 15:
            stat /= .9375
        elif gamesPlayed == 14:
            stat /= .875
        elif gamesPlayed == 13:
            stat /= .8125
        elif gamesPlayed == 12:
            stat /= .75
        elif gamesPlayed == 11:
            stat /= .6875
        elif gamesPlayed == 10:
            stat /= .625
        elif gamesPlayed == 9:
            stat /= .5625
        elif gamesPlayed == 8:
            stat /= .50

        return stat


    """Method that returns a floating point number grade based on the NFL standings of statistics
    in each position category"""
    def grading_method(self, stat, gamesPlayed, param_1, param_2, param_3, param_4):

        appropraited_stat = self.appropriate(gamesPlayed, stat)

        grade = 0

        if appropraited_stat >= param_1:
            if isinstance(self, Quarterback) or isinstance(self, Runningback) or isinstance(self, DefensiveLineman) \
                or isinstance(self, Receiver):
                grade = 2
            elif isinstance(self, Secondary):
                grade = 2.5
            elif isinstance(self, Linebacker):
                grade = 1.664

        elif appropraited_stat < param_1 and stat >= param_2:
            if isinstance(self, Quarterback) or isinstance(self, Runningback) or isinstance(self, DefensiveLineman) \
                or isinstance(self, Receiver):
                grade = 1.5
            elif isinstance(self, Secondary):
                grade = 1.88
            elif isinstance(self, Linebacker):
                grade = 1.249

        elif appropraited_stat < param_2 and stat >= param_3:
            if isinstance(self, Quarterback) or isinstance(self, Runningback) or isinstance(self, DefensiveLineman) \
                or isinstance(self, Receiver):
                grade = 1
            elif isinstance(self, Secondary):
                grade = 1.25
            elif isinstance(self, Linebacker):
                grade = .833

        elif appropraited_stat < param_3 and stat >= param_4:
            if isinstance(self, Quarterback) or isinstance(self, Runningback) or isinstance(self, DefensiveLineman) \
                or isinstance(self, Receiver):
                grade = .5
            elif isinstance(self, Secondary):
                grade = .625
            elif isinstance(self, Linebacker):
                grade = .416

        else:
            grade = 0


        return grade






"""Offensive player parent class"""
class OffensivePlayer(Player):

    def __init__(self, gamesPlayed, touchdowns):
        super().__init__(gamesPlayed)
        self.tds = touchdowns



"""Defensive player parent class"""
class DefensivePlayer(Player):

    def __init__(self, gamesPlayed, totalTackles):
        super().__init__(gamesPlayed)
        self.tackles = totalTackles




"""Quarerback class"""
class Quarterback(OffensivePlayer):

    def __init__(self, gamesPlayed, touchdowns, totalYards, interceptions, completionPercentage, quarterbackRating):
        super().__init__(gamesPlayed, touchdowns)
        self.yards = totalYards
        self.int = interceptions
        self.completion = completionPercentage
        self.qbRating = quarterbackRating



"""Runningback class"""
class Runningback(OffensivePlayer):

    def __init__(self, gamesPlayed, touchdowns, rushingYards, yardsPerAttempt, receptions, receivingYards):
        super().__init__(gamesPlayed, touchdowns)
        self.rushingYds = rushingYards
        self.yardsPer = yardsPerAttempt
        self.rec = receptions
        self.receiving = receivingYards

"""Receiver class"""
class Receiver(OffensivePlayer):

    def __init__(self, gamesPlayed, touchdowns, receptions, receivingYards, yardsPerCatch, catchPercentage):
        super().__init__(gamesPlayed, touchdowns)
        self.receptions = receptions 
        self.yardsPer = yardsPerCatch
        self.catchPercent = catchPercentage
        self.receiving = receivingYards


"""Defensive Lineman class"""
class DefensiveLineman(DefensivePlayer):

    def __init__(self, gamesPlayed, totalTackles, qbSacks, qbHurrys, forcedFumbles, recoveredFumbles):
        super().__init__(gamesPlayed, totalTackles)
        self.sacks = qbSacks
        self.hurrys = qbHurrys
        self.forcedFumbles = forcedFumbles
        self.recoveredFumbles = recoveredFumbles

"""Linebacker class"""
class Linebacker(DefensivePlayer):

    def __init__(self, gamesPlayed, totalTackles, interceptions, forcedFumbles, completionPercentageAllowed, qbHurrys, qbSacks):
        super().__init__(gamesPlayed, totalTackles)
        self.int = interceptions
        self.forcedFumbles = forcedFumbles
        self.completion = completionPercentageAllowed
        self.hurrys = qbHurrys
        self.sacks = qbSacks


"""Secondary class"""
class Secondary(DefensivePlayer):

    def __init__(self, gamesPlayed, totalTackles, interceptions, completionPercentageAllowed, missedTackles):
        super().__init__(gamesPlayed, totalTackles)
        self.int = interceptions
        self.completion = completionPercentageAllowed
        self.missed = missedTackles


"""Function that retrieves statistics pertaining to any NFL skill player from profootballreference.com"""
def retreiveStats(player, first, last, playersTeam):
    urlCounter = 0
    urlCounter2 = 0
    name = ""
    team = ""

    while name != player and team != playersTeam:
        if urlCounter > 9:
            urlCounter2 += 1
            urlCounter = 0
        res = requests.get("https://www.pro-football-reference.com/players/" 
        + last[0] + "/" + last[0:4] + first[0:2] + str(urlCounter2) + str(urlCounter) + ".htm")
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
        soup = BeautifulSoup(res.text, 'html.parser')
        fullName = soup.find('h1', attrs = {'itemprop':'name'})
        try:
            name = fullName.getText()
            teamName = soup.find('span', attrs = {'itemprop' : 'affiliation'})
            team = teamName.getText()
        except(AttributeError):
            name = "No Name"
            team = "No Team"
        urlCounter += 1 

    return soup


#array that holds all nfl skill player positions for grading each player based on their position
playerPositions = ["QB", "RB", "TE", "WR", "DT", "DE", "ILB", "OLB", "S", "CB"]

"""Method that holds the primary functionality of the Pro-Trader program"""
def mainProgram():

    final_grade = 0

    #Prompt the user for the players name 
    playerName = input()

    firstAndLast = playerName.split(" ")

    #retrieve the necessary letters to add to the url 
    firstName = firstAndLast[0]
    firstName.strip()

    #retrive the necessary letter to add to the url 
    lastName = firstAndLast[1]
    lastName.strip()


    #Prompt user for a postion 
    print("Please enter a position from the following list ", end = "")

    #display positions to user
    for i in range(len(playerPositions)):
        print(playerPositions[i] + ", ", end = "")

    positionInput = input("\n")


    #prompt user for team name (last form of authentication)
    teamName = input("Please enter the team that your player currently plays for ex(Atlanta Falcons): ")


    soup = retreiveStats(playerName, firstName, lastName, teamName)

     #Retreive player stats and create objects based on player position 
    if positionInput == "QB":

        total_games_played = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = int(total_games_played.getText())

        total_touchdowns = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'pass_td'})
        touchdowns = int(total_touchdowns.getText())

        total_passing_yards = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'pass_yds'})
        passing_yards = int(total_passing_yards.getText())

        total_interceptions = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'pass_int'})
        interceptions = -(int(total_interceptions.getText()))

        total_completion_percentage = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'pass_cmp_perc'})
        completion_percentage = float(total_completion_percentage.getText())

        total_rating = soup.find('tr', attrs = {'id' : 'passing.2019'}).find('td', attrs = {'data-stat' : 'pass_rating'})
        rating = float(total_rating.getText())

        player_1 = Quarterback(games_played, touchdowns, passing_yards, interceptions, completion_percentage, rating)

        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(touchdowns, games_played, 30, 26, 22, 18) + \
            player_1.grading_method(passing_yards, games_played, 4466, 4002, 3494, 27) + \
                player_1.grading_method(interceptions, games_played, -5, -8, -12, -16) + \
                    player_1.grading_method(completion_percentage, games_played, 69.1, 65.9, 63.2, 60.9) + \
                        player_1.grading_method(rating, games_played, 106.3, 98, 88, 84.3)



    elif positionInput == "RB":

        total_games_played = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = int(total_games_played.getText())

        total_touchdowns = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'rush_td'})
        touchdowns = int(total_touchdowns.getText())

        total_rushing_yards = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'rush_yds'})
        rushing_yards = int(total_rushing_yards.getText())

        rush_yds_per_attempt = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'rush_yds_per_att'})
        ypa = float(rush_yds_per_attempt.getText())

        total_receptions = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'rec'})
        receptions = int(total_receptions.getText())

        total_receving_yards  = soup.find('tr', attrs = {'id' : 'rushing_and_receiving.2019'}).find('td', attrs = {'data-stat' : 'rec_yds'})
        receiving_yards = int(total_receving_yards.getText())

        player_1 = Runningback(games_played, touchdowns, rushing_yards, ypa, receptions, receiving_yards)

        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(touchdowns, games_played, 12, 8, 7, 5) + \
            player_1.grading_method(rushing_yards, games_played, 1230, 1091, 898, 772) + \
                player_1.grading_method(ypa, games_played, 5.1, 4.7, 4.5, 4.2) + \
                    player_1.grading_method(receptions, games_played, 66, 49, 31, 17) + \
                        player_1.grading_method(receiving_yards, games_played, 519, 410, 247, 166)



    elif positionInput == "TE" or positionInput == "WR":

        total_games_played = soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = int(total_games_played.getText())

        total_touchdowns = soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'rec_td'})
    
        touchdowns = int(total_touchdowns.getText())

        total_receptions= soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'rec'})
        rec = int(total_receptions.getText())

        total_receiving_yards = soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'rec_yds'})
        receiving_yards = int(total_receiving_yards.getText())

        receiving_yds_per_reception = soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'rec_yds_per_rec'})
        ypr = float(receiving_yds_per_reception.getText())

        total_catch_percentage = soup.find('tr', attrs = {'id' : 'receiving_and_rushing.2019'}).find('td', attrs = {'data-stat' : 'catch_pct'})
        catch_percentage_white = total_catch_percentage.getText()
        catch_percentage = float(catch_percentage_white.replace("%", ""))


        player_1 = Receiver(games_played, touchdowns, rec, receiving_yards, ypr, catch_percentage)

        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(touchdowns, games_played, 9, 7, 6, 4) + \
            player_1.grading_method(rec, games_played, 97, 83, 66, 42) + \
                player_1.grading_method(receiving_yards, games_played, 1189, 1107, 869, 680) + \
                    player_1.grading_method(ypr, games_played, 16.8, 15.1, 14.1, 12) + \
                        player_1.grading_method(catch_percentage, games_played, 84.1, 78.1, 75.8, 73.5)


    elif positionInput == "DT" or positionInput == "DE":

        total_games_played = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = total_games_played.getText()
        int(games_played)

        total_tackles = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'tackles_combined'})
        tackles = int(total_tackles.getText())

        total_sacks = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'sacks'})
        sacks = float(total_sacks.getText())

        div = soup.find('div', {'id' : 'all_detailed_defense'})
        comment_html = div.find(string = lambda text: isinstance(text, bs4.Comment))
        comment_soup = bs4.BeautifulSoup(comment_html, 'html.parser')

        for tr in comment_soup.find_all('tr'):
            row = [td.text for td in tr.find_all(['td', 'th'])]

        qb_hurry = int(row[-7])

        total_forced_fumbles = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'fumbles_forced'})
        forced_fumbles = int(total_forced_fumbles.getText())


        total_fumbles_recovered = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'fumbles_rec'})
        fumbles_recovered = int(total_fumbles_recovered.getText())


        player_1 = DefensiveLineman(games_played, total_tackles, total_sacks, qb_hurry, forced_fumbles, fumbles_recovered)


        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(tackles, games_played, 50, 34, 26, 10) + \
            player_1.grading_method(sacks, games_played, 4, 3, 2, 1) + \
                player_1.grading_method(qb_hurry, games_played, 7, 5, 3, 2) + \
                    player_1.grading_method(forced_fumbles, games_played, 3, 3, 2, 1) + \
                        player_1.grading_method(fumbles_recovered, games_played, 4, 3, 2, 1)    



    elif positionInput == "ILB" or positionInput == "OLB":

        total_games_played = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = int(total_games_played.getText())

        total_tackles = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'tackles_combined'})
        tackles = int(total_tackles.getText())
        print(tackles)

        total_interceptions = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'def_int'})
        interceptions = int(total_interceptions.getText())

        total_forced_fumbles = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'fumbles_forced'})
        forced_fumbles = int(total_forced_fumbles.getText())


        div = soup.find('div', {'id' : 'all_detailed_defense'})
        comment_html = div.find(string = lambda text: isinstance(text, bs4.Comment))
        comment_soup = bs4.BeautifulSoup(comment_html, 'html.parser')

        for tr in comment_soup.find_all('tr'):
            row = [td.text for td in tr.find_all(['td', 'th'])]

        qb_hurry = int(row[-7])


        for tr in comment_soup.find_all('tr'):
            row = [td.text for td in tr.find_all(['td', 'th'])]

        initial_completion_percentage = row[-17].replace("%", "")
        completion_percentage = -(float(initial_completion_percentage))


        total_sacks = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'sacks'})
        sacks = float(total_sacks.getText())

        player_1 = Linebacker(games_played, total_tackles, total_interceptions, forced_fumbles, completion_percentage, qb_hurry, sacks)

        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(tackles, games_played, 121, 93, 72, 58) + \
            player_1.grading_method(interceptions, games_played, 4, 3, 2, 1) + \
                player_1.grading_method(forced_fumbles, games_played, 4, 3, 2, 1) + \
                    player_1.grading_method(qb_hurry, games_played, 16, 9, 5, 3) + \
                        player_1.grading_method(completion_percentage, games_played, -67.6, -71.1, -76.1, -81) + \
                            player_1.grading_method(sacks, games_played, 10, 8.5, 6.5, 3.5)




    elif positionInput == "CB" or "S":

        total_games_played = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'g'})
        games_played = int(total_games_played.getText())

        total_tackles = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'tackles_combined'})
        tackles = int(total_tackles.getText())

        total_interceptions = soup.find('tr', attrs = {'id' : 'defense.2019'}).find('td', attrs = {'data-stat' : 'def_int'})
        interceptions = int(total_interceptions.getText())


        div = soup.find('div', {'id' : 'all_detailed_defense'})
        comment_html = div.find(string = lambda text: isinstance(text, bs4.Comment))
        comment_soup = bs4.BeautifulSoup(comment_html, 'html.parser')

        for tr in comment_soup.find_all('tr'):
            row = [td.text for td in tr.find_all(['td', 'th'])]

        initial_completion_percentage = row[-17].replace("%", "")
        completion_percentage = -(float(initial_completion_percentage))

        initial_missed_tackles = row[-1].replace("%", "")
        missed_tackles = -(float(initial_missed_tackles))

        player_1 = Secondary(games_played, tackles, interceptions, completion_percentage, missed_tackles)

        #create a player grade by calling the grading method for each player statistical category
        final_grade = player_1.grading_method(tackles, games_played, 105, 76, 65, 51) + \
            player_1.grading_method(interceptions, games_played, 5, 4, 2, 1) + \
                player_1.grading_method(completion_percentage, games_played, -62.2, -65, -68.3, -72.7) + \
                    player_1.grading_method(missed_tackles, games_played, -9.2, -12.1, -16.1, -19.4)




    return final_grade


#Main program
while (True):
    begin = input("Welcome to Pro-Trader. Press enter to begin, press 'q' to quit: ")
    if begin == "q":
        sys.exit(0)
    else:

        print("Please enter the player you wish to trade: ")

        player_one_grade = mainProgram()

        print("Please enter the player you are looking to trade for: ")

        player_two_grade = mainProgram()

    #provide final feedback regarding the trade 

    if player_one_grade > player_two_grade:
        print("\n This trade is determined as poor trade by Pro-Trader")
    elif player_one_grade < player_two_grade:
        print("\n This trade is determined as a benificial trade by Pro-Trader")
    elif player_one_grade == player_two_grade:
        print("\n Both players are of equal value as determined by Pro-Trader")
        

  