#! /usr/bin/env python3

#ACPCHandConverter.py
#Authors: Chris Alvino, Vahe Hagopian, 2016-10-20


from datetime import datetime


class ACPCHandConverter(object):
    """Converts ACPC hand histories into Poker Stars hand histories.

    Attributes:
        infile_name (str): Name of file containing the input hand
            histories in the format used by the Annual Computer
            Poker Competition
        outfile_name (str): Name of file where the output hand
            histories, in Poker Stars format, will be written
        table_num (str): A positive integer that represents a
            unique table number for all of the hands that are in
            the input file
        game_type (str): One letter ('L' or 'N') representing the
            type of hold'em game played in the input file: 'L' is
            limit and 'N' is no-limit
        bb (str): A positive integer multiple of 2 representing the
            size of the big blind for the hands in the input file

        hand_num (int): Unique identifier for each hand in infile_name
        hole_cards (list of str): The players' hole cards listed by
            player
        board_cards (list of str): The board cards listed by street
        players (list of str): The players' names listed by name
        results (list of float): The players' monetary results listed
            by player
        actions_by_round (list of str): The players' actions listed by
            street
        seat_names (list of str): The players' seat assignments
            starting with Seat 1
        positions (dictionary (str->int)): Supported positions are
            mapped to their order within the fields of the input file
        self.out_hh (str:) The output hand history

        convert_hh(): Translates all input hand histories in
            infile_name into output hand histories
        process_hh(): Parses a line of the input hand history
        create_header(): Creates header section of output hand history
        create_actions(): Creates action body of outpuut hand history
        award_pot(): Finalizes an output hand history
    """

    def __init__(self, infile_name, outfile_name, table_num, game_type, bb):
        self.infile_name = infile_name
        self.outfile_name = outfile_name

        if int(table_num) < 1:
            raise ValueError("'table_num' must be a positive integer.")
        self.table_num = int(table_num)

        if game_type != 'L' and game_type != 'N':
            raise ValueError("'game_type' must be 'L' or 'N'.")
        self.game_type = game_type

        if int(bb) < 2 or int(bb) % 2 != 0:
            raise ValueError("'bb' must be a positive integer multiple of 2.")
        self.bb = int(bb)

        self.hand_num = 0
        self.hole_cards = []
        self.board_cards = []
        self.players = []
        self.results = []
        self.actions_by_round = []
        self.seat_names = []
        self.positions = {}
        self.out_hh = ""

    def convert_hh(self):
        """Translates all hand histories in infile_name
        
        Returns:
            None
        Effects:
            Writes to outfile_name
        """

        with open(self.infile_name, 'r') as infile, \
             open(self.outfile_name, 'w') as outfile:

            first_hand = True
            for line in infile:
                in_hh = line.rstrip('\n')
                if in_hh[0:5] != 'STATE':
                    continue

                self.process_hh(in_hh)

                # first hand decides seat assignments
                if first_hand == True:
                    first_hand = False
                    for player in self.players:
                        self.seat_names.append(player)

                self.create_header()
                self.award_pot(*self.create_actions())
                outfile.write(self.out_hh)


    def process_hh(self, in_hh):
        """Extracts the components of each hand from the input hand
           history.

        Args:
            in_hh: A string containing a single input hand history.
        Returns:
            None
        """
        in_hh_split = in_hh.split(':')

        if len(in_hh_split) != 6:
            print(in_hh)
            raise Exception("Incorrect number of fields")

        self.hand_num = int(in_hh_split[1])

        self.players = in_hh_split[5].split('|')
        if len(self.players) > 3 or len(self.players) < 2:
            raise Exception("Invalid number of players")

        self.results = [float(res) for res in in_hh_split[4].split('|')]
        if len(self.results) != len(self.players):
            raise Exception("Number of results != number of players")

        self.actions_by_round = in_hh_split[2].split('/')
        if len(self.actions_by_round) < 1 or len(self.actions_by_round) > 4:
            raise Exception("Invalid number of action rounds")

        # extract hole cards and board cards
        cards = in_hh_split[3].split('|')
        self.hole_cards = [cards[0]]
        if len(self.players) != 2:
            self.hole_cards.append(cards[1])
        cards_last = cards[-1].split('/')
        self.hole_cards.append(cards_last[0])
        self.board_cards = cards_last[1:]
        if len(self.actions_by_round) != len(self.board_cards) + 1:
            raise Exception("Number of action rounds != number of board cards")


    def create_header(self):
        """Create output hand history header

        Returns:
            None
        """
        self.out_hh = "PokerStars Hand #"
        self.out_hh += str(self.table_num) + str(self.hand_num) + ": "

        if self.game_type == 'L':
            self.out_hh += "Hold'em Fixed Limit ($" + str(self.bb)
            self.out_hh += "/$" + str(self.bb * 2) +  ") - "
        else:
            self.out_hh += "Hold'em No Limit ($" + str(int(self.bb / 2))
            self.out_hh += "/$" + str(self.bb) +  ") - "

        self.out_hh += datetime.today().strftime("%Y/%m/%d %H:%M:%S\n")
        self.out_hh += "Table '" + str(self.table_num) + "' "


        # need to do reversed blinds for heads-up play
        if len(self.players) == 2:
            self.positions['utg'] = 1
            self.positions['button'] = 1
            self.positions['small blind'] = 1
            self.positions['big blind'] = 0
            self.out_hh += "2-max "
        else:
            self.positions['utg'] = 2
            self.positions['button'] = len(self.players) - 1
            self.positions['small blind'] = 0
            self.positions['big blind'] = 1
            self.out_hh += "6-max "        

        # determine button player
        for i in range(len(self.players)):
            if self.seat_names[i] == self.players[self.positions['button']]:
                self.out_hh += "Seat #" + str(i+1) + " is the button\n"
                break

        # list seats and corresponding stack sizes
        for i in range(len(self.players)):
            self.out_hh += "Seat " + str(i+1) + ": "
            self.out_hh += self.seat_names[i] + " ($20000 in chips)\n"

        # lists blinds
        self.out_hh += self.players[self.positions['small blind']]
        self.out_hh += ": posts small blind $" + str(int(self.bb / 2)) + "\n"
        self.out_hh += self.players[self.positions['big blind']]
        self.out_hh += ": posts big blind $" + str(self.bb) + "\n"

        # list hole cards
        self.out_hh += "*** HOLE CARDS ***\n"
        for i in range(len(self.players)):
            self.out_hh += "Dealt to " + self.players[i] + " ["
            self.out_hh += self.hole_cards[i][0:2] + " "
            self.out_hh += self.hole_cards[i][2:4] + "]\n"


    def create_actions(self):
        """ Creates the action sequence of the hand history
        Returns:
            players_in_hand (list of bool): list of players who haven't
                folded yet.
            wagered_total (list of int): list of how much each player
                has put into the pot in the current hand.
            current_bet (int): incremental additional amount of the last
                bet or raise
            current_player (int): the first player to show down.
        """
        # flags whether player has folded
        players_in_hand = [True] * len(self.players)

        # amount put into pot by each player over all rounds of betting
        wagered_total = [0] * len(self.players)

        for round in range(len(self.actions_by_round)): # rounds of betting
            if round == 1:
                self.out_hh += "*** FLOP *** ["
                self.out_hh += self.board_cards[0][0:2] + " "
                self.out_hh += self.board_cards[0][2:4] + " "
                self.out_hh += self.board_cards[0][4:6] + "]\n"
            elif round == 2:
                self.out_hh += "*** TURN *** ["
                self.out_hh += self.board_cards[0][0:2] + " "
                self.out_hh += self.board_cards[0][2:4] + " "
                self.out_hh += self.board_cards[0][4:6] + "]"
                self.out_hh += " [" + self.board_cards[1][0:2] + "]\n"
            elif round == 3:
                self.out_hh += "*** RIVER *** ["
                self.out_hh += self.board_cards[0][0:2] + " "
                self.out_hh += self.board_cards[0][2:4] + " "
                self.out_hh += self.board_cards[0][4:6] + "]"
                self.out_hh += " [" + self.board_cards[1][0:2] + "]"
                self.out_hh += " [" + self.board_cards[2][0:2] + "]\n"
            
            # this is a list of lists representing each action in a particular
            # round as a separate list.  In the case of no-limit bets and
            # raises, each sublist will contain two entries, the action and
            # the size.
            actions_this_round = []

            if self.game_type == 'L':
                for action in self.actions_by_round[round]:
                    actions_this_round.append([action])
            else:
                i = 0
                while i < len(self.actions_by_round[round]):
                    if not self.actions_by_round[round][i] == 'r':
                        actions_this_round.append(
                            [self.actions_by_round[round][i]])
                        i += 1
                    else:
                        i += 1
                        bet_size = 0
                        while self.actions_by_round[round][i].isdigit():
                            bet_size = (bet_size * 10 + 
                                        int(self.actions_by_round[round][i]))
                            i += 1
                        actions_this_round.append(['r', bet_size])

            # amount put into pot by each player in current round
            wagered_this_round = [0] * len(self.players)

            if round == 0:
                startingPlayer = self.positions['utg']
                bet_this_round = self.bb
                wagered_this_round[self.positions['small blind']] += \
                                                               int(self.bb / 2)
                wagered_this_round[self.positions['big blind']] += self.bb
            else:
                # heads-up reversed blinds
                if len(self.players) == 2:
                    startingPlayer = self.positions['big blind']
                else:
                    startingPlayer = self.positions['small blind']
                bet_this_round = 0

            if self.game_type == 'L':
                # preflop or flop
                if round == 0 or round == 1:
                    current_bet = self.bb
                else:
                    current_bet = self.bb * 2
            else:
                if round == 0:
                    current_bet = self.bb
                else:
                    current_bet = 0

            current_player = startingPlayer

            # run through all of the actions in the current round
            for act in actions_this_round:

                # index 0 is always a letter (f, c, or r)
                action = act[0]

                # get player who matches above action
                while not players_in_hand[current_player]:
                    current_player = (current_player + 1) % len(self.players)

                amountToCall = (bet_this_round -
                                wagered_this_round[current_player])

                # execute action, record state, and write string
                if action == 'f':
                    players_in_hand[current_player] = False
                    self.out_hh += self.players[current_player] + ": folds\n"
                elif action == 'c': # this is either check or call
                    if amountToCall == 0: # check
                        self.out_hh += self.players[current_player]
                        self.out_hh += ": checks\n"
                    else: # call
                        wagered_this_round[current_player] += amountToCall
                        self.out_hh += self.players[current_player]
                        self.out_hh += ": calls $" + str(amountToCall) + "\n"
                # this is either bet or raise; for no-limit, we look at index 1
                elif action == 'r':
                    if self.game_type == 'N':
                        current_bet = (act[1] - wagered_total[current_player] -
                                       wagered_this_round[current_player] -
                                       amountToCall)
                    wagered_this_round[current_player] += (amountToCall +
                                                           current_bet)
                    bet_this_round += current_bet 

                    # normal raise or preflop big blind option raise
                    if amountToCall > 0 or round == 0:
                        self.out_hh += self.players[current_player]
                        self.out_hh += ": raises $"
                        self.out_hh += str(amountToCall + current_bet)
                        self.out_hh += " to $" + str(bet_this_round) + "\n"
                    else: # bet
                        self.out_hh += self.players[current_player]
                        self.out_hh += ": bets $" + str(current_bet) + "\n"

                # move to next player
                current_player = (current_player + 1) % len(self.players)

                while not players_in_hand[current_player]:
                    current_player = (current_player + 1) % len(self.players)

            for i in range(len(self.players)):
                wagered_total[i] += wagered_this_round[i]

        return players_in_hand, wagered_total, current_bet, current_player


    def award_pot(self, players_in_hand, wagered_total, current_bet,
                  current_player):
        """Finishes the output string with pot and showdown details
    
        Args:
            players_in_hand: A list of bools representing which players
                haven't folded yet.
            wagered_total: A list of integers denoting how much each
                player has put into the pot in the current hand.
            current_bet: An integer denoting the incremental additional
                amount of the last bet or raise
            current_player: an integer representing the first player who
                has to show down.
        Returns:
            None
        """
        players_left = sum(players_in_hand)

        # compute Pot size and Split Pot size
        pot = sum(wagered_total)

        half_pot = float(pot) / 2
        third_pot = pot / 3

        # determine number of winners (multiple if pot is split)
        winners = []
        for i in range(len(self.players)):
            if float(self.results[i]) > 0:
                winners.append([i, self.players[i]])

        if players_left > 1:
            self.out_hh += "*** SHOW DOWN ***\n"
            for i in range(len(self.players)):
                if players_in_hand[(current_player + i) % len(self.players)]:
                    self.out_hh += self.players[(current_player + i) \
                                                 % len(self.players)]
                    self.out_hh += ": shows ["
                    self.out_hh += self.hole_cards[(current_player + i) \
                                                    % len(self.players)][0:2]
                    self.out_hh += " "
                    self.out_hh += self.hole_cards[(current_player + i) \
                                                    % len(self.players)][2:4]
                    self.out_hh += "]\n"
            if len(winners) == 1:
                self.out_hh += winners[0][1] + " collected $"
                self.out_hh += str(pot) + " from pot\n"
            elif len(winners) == 2:
                for winner in winners:
                    self.out_hh += winner[1] + " collected $"
                    self.out_hh += str(round(half_pot, 2)) + " from pot\n"
            elif players_left == 3:
                for i in range(len(self.players)):
                    self.out_hh += self.players[i] + " collected $"
                    self.out_hh += str(third_pot) + " from pot\n"
            else: # blinds chop the pot with no profit
                self.out_hh += self.players[self.positions['small blind']]
                self.out_hh += " collected $" + str(round(half_pot, 2))
                self.out_hh += " from pot\n"
                self.out_hh += self.players[self.positions['big blind']]
                self.out_hh += " collected $" + str(round(half_pot, 2))
                self.out_hh += " from pot\n"
        else:
            pot -= current_bet
            self.out_hh += "Uncalled bet ($" + str(current_bet)
            self.out_hh += ") returned to " + winners[0][1] + '\n'
            self.out_hh += winners[0][1] + " collected $" + str(pot)
            self.out_hh += " from pot"

        final_word = ['mucked'] * len(self.players)
        if len(winners) == 1:
            final_word[winners[0][0]] = 'won ($' + str(pot) + ')'
        elif len(winners) == 2:
            for winner in winners:
                final_word[winner[0]] = 'won ($' + str(round(half_pot)) + ')'
        elif players_left == 3:
            for i in range(len(self.players)):
                final_word[i] = 'won ($' + str(third_pot) + ')'
        else:
            final_word[self.positions['small blind']] = \
                        'won ($' + str(round(half_pot, 2)) + ')'
            final_word[self.positions['big blind']] = \
                        'won ($' + str(round(half_pot, 2)) + ')'


        self.out_hh += "\n*** SUMMARY ***\n"
        self.out_hh += "Total pot $" + str(pot) + "\n"

        if len(self.players) == 2:
            for i in range(len(self.players)):
                for j in range (len(self.players)):
                    if self.seat_names[i] == self.players[j]:
                        for pos_name, pos_value in self.positions.items():
                            if (pos_value == j and
                                (pos_name == 'small blind' or
                                 pos_name == 'big blind')):
                                self.out_hh += "Seat " + str(i + 1) + ": "
                                self.out_hh += self.seat_names[i] + " ("
                                self.out_hh += pos_name + ") "
                                self.out_hh += final_word[j] + '\n'
        else:
            for i in range(len(self.players)):
                for j in range (len(self.players)):
                    if self.seat_names[i] == self.players[j]:
                        for pos_name, pos_value in self.positions.items():
                            if (pos_value == j and
                                (pos_name == 'small blind' or
                                 pos_name == 'big blind' or
                                 pos_name == 'button')):
                                self.out_hh += "Seat " + str(i + 1) + ": "
                                self.out_hh += self.seat_names[i] + " ("
                                self.out_hh += pos_name + ") "
                                self.out_hh += final_word[j] + '\n'
        self.out_hh += "\n\n\n"


def main(argv):
    """
    usage: ACPCHandConverter.py infile_name outfile_name table_num game_type bb
    """
    if len(argv) == 6:
        infile_name, outfile_name, table_num, game_type, bb = argv[1:]
        conv = ACPCHandConverter(infile_name, outfile_name, table_num,
                                 game_type, bb)
        conv.convert_hh()

if __name__ == "__main__":
    from sys import argv
    main(argv)