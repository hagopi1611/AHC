#! /usr/bin/env python3
#Usage: python acpc_hand_converter.py infile outfile
""" This module contains the acpc_hand_converter """

from datetime import datetime


class ACPCHandConverter():
    """ Converts ACPC hand histories into Poker Stars hand histories
    Attributes:
        infile (str): filename containng ACPC hand histories
        outfile (str): filename containing PokerStars hand histories
        first_hand (bool): Flag for reception of first hand history
        shift (int): Number of seats button is shifted from its
            original position in the first hand
        seats (list<str>): The players' seat assignments starting
            with Seat 1
        board_cards (list<str>): The board (community) cards
        players (list<dict>): All the players in the hand; each
            player is a dictionary with six keys:
            0. The player's name
            1. The player's hole cards
            2. What street the player folded on, if at all
            3. The total amount the player has bet in the hand
            4. The player's final net result in the hand
            5. The player's final message to be displayed at summary
        positions (dict str->int): Supported positions are mapped to
            their order within the fields of the input file
        bet_incr (int): The latest bet or raise (aggressive action) in
            the current round of betting
        out_hh (str): The output hand history to be written to outfile
    """
    def __init__(self, infile, outfile, year):
        self.infile = infile
        self.outfile = outfile
        self.year = year
        self.first_hand = True
        self.seats = []
        self.shift = 0
        self.board_cards = []
        self.players = []
        self.positions = {}
        self.bet_incr = 0
        self.out_hh = ""

    def convert_hand_history(self):
        """ Public method to perform hand history conversion.  Calls
           all of the other methods in this class.
        """
        with open(self.infile, "r") as ifile,\
             open(self.outfile, "w") as ofile:
            for line in ifile:
                # Extract game parameters from first line of input file
                if line[0:6] == "# name":
                    game_param = line.rstrip("\n").split(" ")
                    ### table_num = game_param[-1]

                    ## infile_split = self.infile.split(".")
                    ## if len(infile_split[-3]) == 1:
                    ##     table_num = "0" + infile_split[-3] + infile_split[-2]
                    ## else:
                    ##     table_num = infile_split[-3] + infile_split[-2]

                    infile_split = self.infile.split(".")
                    infile_subsplit1 = infile_split[-3].split("-")
                    infile_subsplit2 = infile_split[-2].split("-")
                    table_num = self.year + infile_subsplit1[-1] + infile_subsplit2[-1]

                    # if len(infile_split[-2]) == 1:
                    #     table_num = "0" + '1' + infile_split[-2] + infile_split[-1]
                    # else:
                    #     table_num = '1' + infile_split[-2] + infile_split[-1]

                    # game_type = game_param[3].split(".")[1]
                    game_type = "limit"
                    # infile_split = game_param[2].split("_")
                    # table_num = infile_split[-1]
                    continue
                # Wait for hand histories to start
                if line[0:5] != "STATE":
                    continue
                # Translate each hand history
                hand_num, actions = self.process_hh(line)
                self.create_header(table_num, hand_num, game_type)
                for street in range(len(actions)):
                    self.create_board(street)
                    bet_in_round, first_player =\
                        self.set_betting(game_type, street)
                    cur_player = self.do_betting(game_type, actions, street,
                                                 bet_in_round, first_player)
                pot = self.showdown(cur_player)
                self.summary(street, pot)
                ofile.write(self.out_hh)

    def process_hh(self, line):
        """ Parse and tokenize one hand history
        Args:
            line (str): A line from the input file
        """
        hand_hist = line.rstrip("\n").split(":")
        hand_num = hand_hist[1]
        actions = hand_hist[2].split("/")
        cards = hand_hist[3].split("|")
        cards_tail = cards[-1].split("/")
        hole_cards = cards[0:-1] + [cards_tail[0]]
        self.board_cards = cards_tail[1:]
        results = [float(result) for result in hand_hist[4].split("|")]
        names = hand_hist[5].split("|")
        self.players = [{"name": names[i], "hole_cards": hole_cards[i],\
                        "street_folded": 4, "total_bet": 0,\
                        "result": results[i], "final_word": "mucked"}\
                        for i in range(len(names))]
        if self.first_hand:
            self.seats = [player["name"] for player in self.players]
            self.first_hand = False
        for i, player in enumerate(self.players):
            if self.seats[0] == player["name"]:
                self.shift = i
        # Reverse blinds positional structure
        if len(self.players) == 2:
            self.positions = {
                "utg": 1,
                "button": 1,
                "small blind": 1,
                "big blind": 0
            }
        # Normal blinds positional structure
        else:
            self.positions = {
                "utg": 2,
                "button": len(names) - 1,
                "small blind": 0,
                "big blind": 1
            }
        return (hand_num, actions)

    def create_header(self, table_num, hand_num, game_type):
        """ Create initial part of hand history
        Args:
            table_num (str): Represents a unique table number for all
                of the hands that are in the input file
            hand_num (str): Represents a unique number for each hand
                in the hand history
            game_type (str): "limit" or "nolimit" representing the
                type of hold'em game
        """
        if game_type == "limit":
            big_blind = 10
        else:
            big_blind = 100
        self.out_hh = "PokerStars Game #"
        self.out_hh += table_num + hand_num.zfill(4)
        self.out_hh += ":  "
        if game_type == "limit":
            self.out_hh += "Hold'em Limit ($" + str(big_blind)
            self.out_hh += "/$" + str(big_blind * 2) +  ") - "
        else:
            self.out_hh += "Hold'em No Limit ($"
            self.out_hh += str(big_blind // 2)
            self.out_hh += "/$" + str(big_blind) +  " USD) - "
        self.out_hh += datetime.today().strftime("%Y/%m/%d %H:%M:%S ET\n")
        self.out_hh += "Table '" + table_num + "' "
        if len(self.players) == 2:
            self.out_hh += "2-max "
        else:
            self.out_hh += "6-max "
        ind = (self.positions["button"] - self.shift) % len(self.players)
        self.out_hh += "Seat #" + str(ind+1) + " is the button\n"
        for i, name in enumerate(self.seats):
            self.out_hh += "Seat " + str(i+1) + ": "
            self.out_hh += name + " ($20000 in chips)\n"
        self.out_hh += self.players[self.positions["small blind"]]["name"]
        self.out_hh += ": posts small blind $" + str(big_blind // 2) + "\n"
        self.out_hh += self.players[self.positions["big blind"]]["name"]
        self.out_hh += ": posts big blind $" + str(big_blind) + "\n"
        self.out_hh += "*** HOLE CARDS ***\n"
        for player in self.players:
            self.out_hh += "Dealt to " + player["name"] + " ["
            self.out_hh += player["hole_cards"][0:2] + " "
            self.out_hh += player["hole_cards"][2:4] + "]\n"

    def create_board(self, street):
        """ Create board for each postflop street
        Args:
            street (int): Round of betting: 0->preflop, 1->flop,
                2->turn, 3->river
        """
        if street == 1:
            self.out_hh += "*** FLOP *** ["
            self.out_hh += self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6] + "]\n"
        elif street == 2:
            self.out_hh += "*** TURN *** ["
            self.out_hh += self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6] + "]"
            self.out_hh += " [" + self.board_cards[1][0:2] + "]\n"
        elif street == 3:
            self.out_hh += "*** RIVER *** ["
            self.out_hh += self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6] + "]"
            self.out_hh += " [" + self.board_cards[1][0:2] + "]"
            self.out_hh += " [" + self.board_cards[2][0:2] + "]\n"

    def set_betting(self, game_type, street):
        """ Initializes state variables for betting round
        Args:
            game_type (str): "limit" or "nolimit" representing the
                type of hold'em game
            street (int): Round of betting: 0->preflop, 1->flop,
                2->turn, 3->river
        """
        if game_type == "limit":
            big_blind = 10
        else:
            big_blind = 100
        bet_in_round = [0] * len(self.players)
        if street == 0:
            first_player = self.positions["utg"]
            bet_in_round[self.positions["small blind"]] += big_blind // 2
            bet_in_round[self.positions["big blind"]] += big_blind
        else:
            if len(self.players) == 2:
                first_player = self.positions["big blind"]
            else:
                first_player = self.positions["small blind"]
        if game_type == "limit":
            if street in (0, 1):
                self.bet_incr = big_blind
            else:
                self.bet_incr = big_blind * 2
        else:
            if street == 0:
                self.bet_incr = big_blind
            else:
                self.bet_incr = 0
        return bet_in_round, first_player

    def do_betting(self, game_type, actions, street, bet_in_round,
                   first_player):
        """ Creates players' actions for the current round of betting
        Args:
            game_type (str): "limit" or "nolimit" representing the
                type of hold'em game
            actions (list<str>): Players actions and bet/raise
                sizes over all rounds
            bet_in_round (list<int>): The amount wagered on the
                current found by each player
            first_player (int): First player to act in the
                current round
        """
        cur_player = first_player
        i = 0
        while i < len(actions[street]):
            # Cycle past players who have folded
            while self.players[cur_player]["street_folded"] != 4:
                cur_player = (cur_player + 1) % len(self.players)
            amt_to_call = max(bet_in_round) - bet_in_round[cur_player]
            #Player folds
            if actions[street][i] == "f":
                self.out_hh += self.players[cur_player]["name"] + ": folds\n"
                self.players[cur_player]["street_folded"] = street
            # Passive action: interpret as either a check or a call
            elif actions[street][i] == "c":
                if amt_to_call == 0:
                    self.out_hh += self.players[cur_player]["name"] + ": checks\n"
                else:
                    self.out_hh += self.players[cur_player]["name"]
                    self.out_hh += ": calls $" + str(amt_to_call) + "\n"
                    bet_in_round[cur_player] += amt_to_call
            # Aggressive action
            else:
                # Extract bet/raise size, for no-limit, from action string
                if game_type == "nolimit":
                    i += 1
                    bet_size = 0
                    while actions[street][i].isdigit():
                        bet_size = (bet_size * 10
                                    + int(actions[street][i]))
                        i += 1
                    i -= 1
                    self.bet_incr = (bet_size
                                     - self.players[cur_player]["total_bet"]
                                     - bet_in_round[cur_player]
                                     - amt_to_call)
                bet_in_round[cur_player] += amt_to_call + self.bet_incr
                # Interpret action as either a raise or a bet
                if amt_to_call > 0 or street == 0:
                    self.out_hh += self.players[cur_player]["name"]
                    self.out_hh += ": raises $"
                    self.out_hh += str(self.bet_incr)
                    self.out_hh += " to $" + str(max(bet_in_round)) + "\n"
                else:
                    self.out_hh += self.players[cur_player]["name"]
                    self.out_hh += ": bets $" + str(self.bet_incr) + "\n"
            cur_player = (cur_player + 1) % len(self.players)
            i += 1
        for i, player in enumerate(self.players):
            player["total_bet"] += bet_in_round[i]
        return cur_player

    def showdown(self, cur_player):
        """ Creates showdown portion of hand history
        Args:
            cur_player (int): The index of the next player to act, for
                purposes of showdown display ordering
        """
        # Calculate final pot size
        pot = sum([player["total_bet"] for player in self.players])
        # See who's still in
        still_in = [player["street_folded"] == 4 for player in self.players]
        # Case of no showdown
        if still_in.count(True) == 1:
            pot -= self.bet_incr
            player = self.players[still_in.index(True)]
            self.out_hh += "Uncalled bet ($" + str(self.bet_incr)
            self.out_hh += ") returned to " + player["name"] + "\n"
            self.out_hh += player["name"] + " collected "
            self.out_hh += "$" + str(pot) + " from pot\n"
            player["final_word"] = "collected ($" + str(pot) + ")"
        # Case of showdown
        else:
            self.out_hh += "*** SHOW DOWN ***\n"
            winners = []
            for i in range(len(self.players)):
                ind = (cur_player + i) % len(self.players)
                if still_in[ind]:
                    self.out_hh += self.players[ind]["name"]
                    self.out_hh += ": shows ["
                    self.out_hh += self.players[ind]["hole_cards"][0:2]
                    self.out_hh += " "
                    self.out_hh += self.players[ind]["hole_cards"][2:4]
                    self.out_hh += "]\n"
                    if self.players[ind]["result"] >= 0:
                        winners.append(self.players[ind])
            for winner in winners:
                self.out_hh += winner["name"] + " collected $"
                if len(winners) == 1:
                    self.out_hh += str(pot)
                    winner["final_word"] = "won ($" + str(pot) + ")"
                else:
                    self.out_hh += "{:.4f}".format(pot/len(winners))
                    winner["final_word"] = ("won ($" +
                                            "{:.4f}".format(pot/len(winners))
                                            + ")")
                self.out_hh += " from pot\n"
        # Losers' spam
        folding_words = ["folded before Flop",
                         "folded on the Flop",
                         "folded on the Turn",
                         "folded on the River"
                        ]
        for player in self.players:
            if player["street_folded"] < 4:
                player["final_word"] = folding_words[player["street_folded"]]
                if player["total_bet"] == 0:
                    player["final_word"] += " (didn't bet)"
        return pot

    def summary(self, street, pot):
        """ Create concluding summary section
        Args:
            street (int): Round of betting: 0->preflop, 1->flop,
                2->turn, 3->river
            pot (int): The size of the final pot
        """
        self.out_hh += "*** SUMMARY ***\n"
        self.out_hh += "Total pot $" + str(pot) + "\n"
        if street == 1:
            self.out_hh += "Board [" + self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6] + "]\n"
        elif street == 2:
            self.out_hh += "Board [" + self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6]
            self.out_hh += " " + self.board_cards[1][0:2] + "]\n"
        elif street == 3:
            self.out_hh += "Board [" + self.board_cards[0][0:2] + " "
            self.out_hh += self.board_cards[0][2:4] + " "
            self.out_hh += self.board_cards[0][4:6]
            self.out_hh += " " + self.board_cards[1][0:2]
            self.out_hh += " " + self.board_cards[2][0:2] + "]\n"
        for i, name in enumerate(self.seats):
            self.out_hh += "Seat " + str(i + 1) + ": " + name + " "
            if (self.positions["button"] - self.shift) % len(self.seats) == i:
                self.out_hh += "(" + "button" + ") "
            if (self.positions["small blind"] - self.shift) % len(self.seats)\
                == i:
                self.out_hh += "(" + "small blind" + ") "
            if (self.positions["big blind"] - self.shift) % len(self.seats)\
                == i:
                self.out_hh += "(" + "big blind" + ") "
            self.out_hh += self.players[(i + self.shift) % len(self.seats)]\
                           ["final_word"] + "\n"
        self.out_hh += "\n\n\n"


def main(args):
    """ Instantiate and run the hand converter """
    converter = ACPCHandConverter(*args[1:])
    converter.convert_hand_history()


if __name__ == "__main__":
    from sys import argv
    main(argv)
