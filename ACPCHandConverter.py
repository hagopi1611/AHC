#! /usr/bin/env python3

#ACPCHandConverter.py
#Usage: ACPCHandHistory.py infile outfile table_num game_type
#Authors: Chris Alvino, Vahe Hagopian 2016-10-20
#Refactored 2017-02-08


from datetime import datetime


class ACPCHandConverter(object):
    """Converts ACPC hand histories into Poker Stars hand histories

    Attributes:
        infile (str): Name of file containing the input hand
            histories in the format used by the Annual Computer
            Poker Competitioninput file
        outfile (str): Name of file where the output hand
            histories, in Poker Stars format, will be written
        table_num (str): A positive integer that represents a
            unique table number for all of the hands that are in
            the input file
        game_type (str): One letter ('L' or 'N') representing the
            type of hold'em game played in the input file: 'L' is
            limit and 'N' is no-limit
        bb (int): A positive integer representing the size of the
            big blind for the hands in the input file
        players (list<str>): The players' names listed by name
        np (int):
        still_in (list<bool>): Flags that denote whether a player
            has not yet folded in the current hand
        total_bet (list<int>): The total amount wagered by each
            player in the current hand
        hc (list<str>): The players' hole cards listed by
            player
        positions (dictionary str->int): Supported positions are
            mapped to their order within the fields of the input file
        seat_names (list<str>): The players' seat assignments
            starting with Seat 1
        street (int): Round of betting: 0->preflop, 1->flop, 2->turn, 3->river
        bet_incr (int): The latest bet or raise (aggressive action)
            in the current round of betting
        out_hh (str): The output hand history to be written to outfile
    """

    def __init__(self, infile, outfile, table_num, game_type):
        self.infile = infile
        self.outfile = outfile
        self.table_num = int(table_num)
        self.game_type = game_type
        if game_type == 'L':
            self.bb = 10
        else:
            self.bb = 100
        self.players = []
        self.np = 0
        self.still_in = []
        self.total_bet = []
        self.hc = []
        self.positions = {}
        self.seat_names = []
        self.street = 0
        self.bet_incr = 0
        self.out_hh = ""

    def convert_hh(self):
        """Public method to perform hand history conversion.  Calls all
        of the other methods in this class.
        """
        
        with open(self.infile, 'r') as ifile, open(self.outfile, 'w') as ofile:
            first_hand = True
            for line in ifile:
                if line[0:5] != 'STATE':
                    continue
                hand_num, actions, results, bc = self.process_hh(line)
                if first_hand == True:
                    first_hand = False
                    for player in self.players:
                        self.seat_names.append(player)
                self.create_header(hand_num)
                for self.street in range(len(actions)):
                    self.create_board(bc)
                    cur_player = self.create_betting(actions,\
                                                     *self.setup_betting())
                self.showdown(results, cur_player)
                ofile.write(self.out_hh)

    def process_hh(self, line):
        """Parse and Tokenize a line from the input hand history

        Args:
            line (str): An input hand history
        """
        
        hh = line.rstrip('\n').split(':')
        hand_num = int(hh[1])
        actions = hh[2].split('/')
        results = [float(result) for result in hh[4].split('|')]
        self.players = hh[5].split('|')
        self.np = len(self.players)
        self.still_in = [True] * self.np
        self.total_bet = [0] * self.np
        if self.np == 2:
            self.positions['utg'] = 1
            self.positions['button'] = 1
            self.positions['small blind'] = 1
            self.positions['big blind'] = 0
        else:
            self.positions['utg'] = 2
            self.positions['button'] = self.np - 1
            self.positions['small blind'] = 0
            self.positions['big blind'] = 1
        cards = hh[3].split('|')
        cards_last = cards[-1].split('/')
        self.hc = [cards[0]]
        if self.np != 2:
            self.hc.append(cards[1])
        self.hc.append(cards_last[0])
        bc = cards_last[1:]
        return hand_num, actions, results, bc

    def create_header(self, hand_num):
        """Print initial part of hand history

        Args:
            hand_num (int): The unique number of the current hand
        """
        
        self.out_hh = "PokerStars Hand #"
        self.out_hh += str(self.table_num) + str(hand_num).zfill(4) + ": "
        if self.game_type == 'L':
            self.out_hh += "Hold'em Fixed Limit ($" + str(self.bb)
            self.out_hh += "/$" + str(self.bb * 2) +  ") - "
        else:
            self.out_hh += "Hold'em No Limit ($" + str(int(self.bb / 2))
            self.out_hh += "/$" + str(self.bb) +  ") - "
        self.out_hh += datetime.today().strftime("%Y/%m/%d %H:%M:%S\n")
        self.out_hh += "Table '" + str(self.table_num) + "' "
        if self.np == 2:
            self.out_hh += "2-max "
        else:
            self.out_hh += "6-max "
        for i in range(self.np):
            if self.seat_names[i] == self.players[self.positions['button']]:
                self.out_hh += "Seat #" + str(i+1) + " is the button\n"
                break
        for i in range(self.np):
            self.out_hh += "Seat " + str(i+1) + ": "
            self.out_hh += self.seat_names[i] + " ($20000 in chips)\n"
        self.out_hh += self.players[self.positions['small blind']]
        self.out_hh += ": posts small blind $" + str(int(self.bb / 2)) + "\n"
        self.out_hh += self.players[self.positions['big blind']]
        self.out_hh += ": posts big blind $" + str(self.bb) + "\n"
        self.out_hh += "*** HOLE CARDS ***\n"
        for i in range(self.np):
            self.out_hh += "Dealt to " + self.players[i] + " ["
            self.out_hh += self.hc[i][0:2] + " "
            self.out_hh += self.hc[i][2:4] + "]\n"

    def create_board(self, bc):
        """Print board

        Args:
            bc (list<str>): The board (community) cards
        """
        
        if self.street == 1:
            self.out_hh += "*** FLOP *** ["
            self.out_hh += bc[0][0:2] + " "
            self.out_hh += bc[0][2:4] + " "
            self.out_hh += bc[0][4:6] + "]\n"
        elif self.street == 2:
            self.out_hh += "*** TURN *** ["
            self.out_hh += bc[0][0:2] + " "
            self.out_hh += bc[0][2:4] + " "
            self.out_hh += bc[0][4:6] + "]"
            self.out_hh += " [" + bc[1][0:2] + "]\n"
        elif self.street == 3:
            self.out_hh += "*** RIVER *** ["
            self.out_hh += bc[0][0:2] + " "
            self.out_hh += bc[0][2:4] + " "
            self.out_hh += bc[0][4:6] + "]"
            self.out_hh += " [" + bc[1][0:2] + "]"
            self.out_hh += " [" + bc[2][0:2] + "]\n"
        
    def setup_betting(self):
        """Initializes state variables for betting round"""
        
        bet_in_round = [0] * self.np
        if self.street == 0:
            starting_player = self.positions['utg']
            bet_in_round[self.positions['small blind']] += int(self.bb / 2)
            bet_in_round[self.positions['big blind']] += self.bb
        else:
            if self.np == 2:
                starting_player = self.positions['big blind']
            else:
                starting_player = self.positions['small blind']
        if self.game_type == 'L':
            if self.street == 0 or self.street == 1:
                self.bet_incr = self.bb
            else:
                self.bet_incr = self.bb * 2
        else:
            if self.street == 0:
                self.bet_incr = self.bb
            else:
                self.bet_incr = 0
        return bet_in_round, starting_player

    def create_betting(self, actions, bet_in_round, starting_player):
        """Prints players' actions for current round of betting

        There are five state variables used to this end:
            still_in (list<bool>): Has the player folded yet?
            amt_to_call (int): How much to call all bets
            bet_in_round (list<int>): Total wagered by each player this round
            cur_player (int): Who is the action is on?
            total_bet (list<int>): Total wagered by each player over all rounds

        Args:
            actions (list<str>): Players actions and bet/raise sizes over
                all rounds
            bet_in_round (list<int>): The amount wagered on the current
                found by each player
            starting_player (int): First player to act in the current round
        """
        cur_player = starting_player
        i = 0
        while i < len(actions[self.street]):

            # Cycle past players who have folded
            while not self.still_in[cur_player]:
                cur_player = (cur_player + 1) % self.np

            # Update state variable
            amt_to_call = max(bet_in_round) - bet_in_round[cur_player]

            #Player folds
            if actions[self.street][i] == 'f':
                self.out_hh += self.players[cur_player] + ": folds\n"

                # Update state variable
                self.still_in[cur_player] = False

            # Passive action: interpret as either a check or a call
            elif actions[self.street][i] == 'c':
                if amt_to_call == 0:
                    self.out_hh += self.players[cur_player] + ": checks\n"
                else:
                    self.out_hh += self.players[cur_player]
                    self.out_hh += ": calls $" + str(amt_to_call) + "\n"

                    # Update state variable
                    bet_in_round[cur_player] += amt_to_call

            # Aggressive action
            else:

                # Extract bet/raise size, for no-limit, from action string
                if self.game_type == 'N':
                    i += 1
                    bet_size = 0
                    while actions[self.street][i].isdigit():
                        bet_size = (bet_size * 10
                                    + int(actions[self.street][i]))
                        i += 1
                    i -= 1
                    self.bet_incr = (bet_size
                                     - self.total_bet[cur_player]
                                     - bet_in_round[cur_player]
                                     - amt_to_call)

                # Update state variable
                bet_in_round[cur_player] += amt_to_call + self.bet_incr

                # Interpret action as either a raise or a bet
                if amt_to_call > 0 or self.street == 0:
                    self.out_hh += self.players[cur_player]
                    self.out_hh += ": raises $"
                    self.out_hh += str(amt_to_call + self.bet_incr)
                    self.out_hh += " to $" + str(max(bet_in_round)) + "\n"
                else:
                    self.out_hh += self.players[cur_player]
                    self.out_hh += ": bets $" + str(self.bet_incr) + "\n"

            # Update state variable
            cur_player = (cur_player + 1) % self.np            
            i += 1

        # Update stat variable
        for i in range(self.np):
            self.total_bet[i] += bet_in_round[i]
            
        return cur_player

    def showdown(self, results, cur_player):
        """Prints concluding portion of hand history

        Args:
            results (list<float>): Net win/loss of each player
            cur_player (int): The next player to act, for purposes of
                showdown display ordering
        """
        players_left = sum(self.still_in)
        pot = sum(self.total_bet)

        # Determine winners
        winners = []
        for i in range(self.np):
            if float(results[(cur_player + i) % self.np]) > 0.001:
                winners.append(self.players[(cur_player + i) % self.np])
        if len(winners) == 0:
            for i in range(self.np):
                if self.still_in[(cur_player + i) % self.np]:
                    winners.append(self.players[(cur_player + i) % self.np])

        # Winner spam for case of No Showdown
        if players_left == 1:
            pot -= self.bet_incr
            self.out_hh += "Uncalled bet ($" + str(self.bet_incr)
            self.out_hh += ") returned to " + winners[0] + "\n"
            self.out_hh += winners[0] + " collected "
            self.out_hh += "$" + str(pot) + " from pot"

        # Case of Showdown
        else:
            self.out_hh += "*** SHOW DOWN ***\n"
            for i in range(self.np):
                if self.still_in[(cur_player + i) % self.np]:
                    self.out_hh += self.players[(cur_player + i) % self.np]
                    self.out_hh += ": shows ["
                    self.out_hh += self.hc[(cur_player + i) % self.np][0:2]
                    self.out_hh += " "
                    self.out_hh += self.hc[(cur_player + i) % self.np][2:4]
                    self.out_hh += "]\n"
            for winner in winners:
                self.out_hh += winner + " collected $"
                self.out_hh += str(pot / len(winners))
                self.out_hh += " from pot\n"

        # Summary section
        final_word = {}
        for player in self.players:
            final_word[player] = 'mucked'
        for winner in winners:
            final_word[winner] = 'won ($' + str(pot / len(winners)) + ')'
        self.out_hh += "\n*** SUMMARY ***\n"
        self.out_hh += "Total pot $" + str(pot) + "\n"
        for i in range(self.np):
            self.out_hh += "Seat " + str(i + 1) + ": "
            self.out_hh += self.seat_names[i] + " ("
            for pos in self.positions.keys():
                if (self.players[self.positions[pos]] == self.seat_names[i])\
                   and (pos == 'small blind' or pos == 'big blind'\
                        or (pos == 'button' and self.np == 3)):
                    self.out_hh += pos + ") "
            self.out_hh += final_word[self.seat_names[i]] + '\n'
        self.out_hh += "\n\n\n"


def main(argv):
    converter = ACPCHandConverter(*argv[1:])
    converter.convert_hh()


if __name__ == "__main__":
    from sys import argv
    main(argv)
