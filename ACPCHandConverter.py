"""
ACPCHandConverter.py

Converts ACPC hand histories into Poker Stars hand histories
"""

import sys
import datetime
import time

output_string = ""

def main(argv):     
    """Converts ACPC hand histories into Poker Stars hand histories

    Args:
        input_filename: A file containing input hand histories in the format
            used by the Annual Computer Poker Competition
        output_filename: The file in which the output hand histories in Poker
            Stars format will be written
        table_number: A positive integer that represents a unique table
            number for all of the hands that are in the input file
        game_type: One letter ('L' or 'N') representing the type of hold'em
            game played in the input file: 'L' is limit and 'N' is no-limit
        big_blind: A positive integer number representing the size of the big
            blind for all of the hands that are in the input file
    
    Returns:
        None

    Effects:
        Writes converted hand histories to the output file 'output_filename'
    """
    if len(argv) != 5:
        raise Exception("Usage: ACPCHandConverter input_file output_file " +
                        "table_number game_type big_blind\n")
        
    input_filename = argv[0]
    output_filename = argv[1]
    
    table_number = int(argv[2])
    if table_number < 1:
            raise ValueError("Argument 'table_number' should be a positive " +
                             "integer\n")
        
    game_type = argv[3]
    if game_type != 'L' and game_type != 'N':
        raise ValueError("Argument 'game_type' must be 'L' or 'N'.\n")

    big_blind = int(argv[4])
    if big_blind < 2 or big_blind % 2 != 0:
        raise ValueError("Argument 'big_blind' should be a positive " +
                         "integer multiple of 2.\n")

    hand_counter = 1

    with open(input_filename,'r') as input_file:
        with open(output_filename, 'w') as output_file:
            for line in input_file:
                if hand_counter == 10000:
                    raise Exception("Input file too long")
                
                hand_history = line.rstrip('\n')
                if hand_history[0:5] != 'STATE':
                    continue

                processed_line = process_line(hand_history)
                
                hand_number = processed_line[0]
                actions_by_round = processed_line[1]
                hole_cards = processed_line[2]
                board_cards = processed_line[3]
                results = processed_line[4]
                players = processed_line[5]
                
                # use first hand to decide seat assignments
                if hand_counter == 1:
                    seat_names = []
                    for i in range(len(players)):
                        seat_names.append(players[i])
                
                positions = create_header(table_number, game_type, big_blind,
                                          hand_number, hole_cards, players,
                                          seat_names)

                showdown_state = create_actions(game_type, big_blind,
                                                actions_by_round, hole_cards,
                                                board_cards, players,
                                                seat_names, positions)
                               
                players_in_hand = showdown_state[0]
                wagered_total = showdown_state[1]
                current_bet = showdown_state[2]
                current_player = showdown_state[3]
                                 
                award_pot(hole_cards, results, players, seat_names, positions,
                         players_in_hand, wagered_total, current_bet,
                         current_player)

                output_file.write(output_string)
                hand_counter += 1

                           
def process_line(hand_history):
    """Extracts the components of each hand from the input hand history.

    Args:
        hand_history: A string containing a single input hand history.
        
    Returns:
        processed_line: A tuple of length 6 containing:
            hand_number: An integer that uniquely identifies each hand
            actions_by_round: A list of strings representing actions by street
            hole_cards: A list of strings containing the players' hole cards
            board_cards: A list of strings containing the board cards by street
            results: A list of floats containing the players' monetary results
            players: A list of strings containing the players' names
    """
    hand_history_split = hand_history.split(':')

    if len(hand_history_split) != 6:
        print(hand_history)
        raise Exception("Incorrect number of fields")

    hand_number = int(hand_history_split[1])

    players = hand_history_split[5].split('|')
    if len(players) > 3 or len(players) < 2:
        raise Exception("Invalid number of players")
    
    results = [float(result) for result in hand_history_split[4].split('|')]
    if len(results) != len(players):
        raise Exception("Number of results and number of players don't match")

    actions_by_round = hand_history_split[2].split('/')
    if len(actions_by_round) < 1 or len(actions_by_round) > 4:
        raise Exception("Invalid number of action rounds")

    # extract hole cards and board cards
    cards = hand_history_split[3].split('|')
    hole_cards = []
    hole_cards.append(cards[0])
    if len(players) == 2:
        cards_last = cards[1].split('/')
    else:
        hole_cards.append(cards[1])
        cards_last = cards[2].split('/')
    hole_cards.append(cards_last[0])
    board_cards = cards_last[1:]
    if len(actions_by_round) != len(board_cards) + 1:
        raise Exception("Number of action rounds doesn't match number of " +
                        "board cards")

    processed_line = (hand_number, actions_by_round, hole_cards,
                      board_cards, results, players)
    
    return processed_line


def create_header(table_number, game_type, big_blind, hand_number, hole_cards,
                 players, seat_names):
    """Create output hand history header
    
    Args:
        table_number: A positive integer that represents a unique table
            number for all of the hands that are in the input file
        game_type: One letter ('L' or 'N') representing the type of hold'em
            game played in the input file: 'L' is limit and 'N' is no-limit
        big_blind: A positive integer number representing the size of the big
            blind for all of the hands that are in the input file
        hand_number: An integer that uniquely identifies each hand
        hole_cards: A list of strings containing the players' hole cards
        players: A list of strings containing the players' names
        seat_names: A list of strings dictating the players' seat assignments
        
    Returns:
        positions: A dictionary mapping the supported positions to their order
            within the fields of the input file

    Effects:
        prints to 'output_string'
    """
    global output_string
    
    output_string = ("PokerStars Hand #" + str(table_number) +
                     str(hand_number) + ": ")

    if game_type == 'L':
        output_string += ("Hold'em Fixed Limit ($" + str(big_blind) + "/$" +
                          str(big_blind * 2) +  ") - ")
    else:
        output_string += ("Hold'em No Limit ($" + str(int(big_blind / 2)) +
                          "/$" + str(big_blind) +  ") - ")

    dateNow = datetime.datetime.fromtimestamp(time.time())                        
    output_string += dateNow.strftime("%Y/%m/%d %H:%M:%S\n")
    output_string += "Table '" + str(table_number) + "' "

    # Create dictionary with positions as the keys and the index within
    # each field corresponding to that position as the values
    positions = {}
    
    # need to do reversed blinds for heads-up play
    if len(players) == 2:
        positions['utg'] = 1
        positions['button'] = 1
        positions['small blind'] = 1
        positions['big blind'] = 0
        output_string += "2-max "
    else:
        positions['utg'] = 2
        positions['button'] = len(players) - 1
        positions['small blind'] = 0
        positions['big blind'] = 1
        output_string += "6-max "        
        
    # determine button player
    for i in range(len(players)):
        if seat_names[i] == players[positions['button']]:
            output_string += "Seat #" + str(i+1) + " is the button\n"
            break

    # list seats and corresponding stack sizes
    for i in range(len(players)):
        output_string += ("Seat " + str(i+1) + ": " + seat_names[i] +
                      " ($20000 in chips)\n")

    # lists blinds
    output_string += (players[positions['small blind']] +
                      ": posts small blind $" + str(int(big_blind / 2)) + "\n")
    output_string += (players[positions['big blind']] + ": posts big blind $" +
                      str(big_blind) + "\n")

    # list hole cards
    output_string += "*** HOLE CARDS ***\n"
    for i in range(len(players)):
        output_string += "Dealt to " + players[i] + " ["
        output_string += hole_cards[i][0:2] + " " + hole_cards[i][2:4] + "]\n"
    
    return positions


def create_actions(game_type, big_blind, actions_by_round, hole_cards,
                  board_cards, players, seat_names, positions):
    """ Creates the action sequence of the hand history

    Args:
        game_type: One letter ('L' or 'N') representing the type of hold'em
            game played in the input file: 'L' is limit and 'N' is no-limit
        big_blind: A positive integer number representing the size of the big
            blind for all of the hands that are in the input file
        actions_by_round: A list of strings representing actions by street
        hole_cards: A list of strings containing the players' hole cards
        board_cards: A list of strings containing the board cards by street
        players: A list of strings containing the players' names
        seat_names: A list of strings dictating the players' seat assignments.
            The list returned is empty for all but the first hand, which is
            used to set the seat assignments.
        positions: A dictionary mapping the supported positions to their order
            within the fields of the input file
       
    Returns:
        showdown_state: A tuple of length 4 containing:
            players_in_hand: A list of bools representing which players haven't
                folded yet.
            wagered_total: A list of integers denoting how much each
                player has put into the pot in the current hand.
            current_bet: An integer denoting the incremental additional amount
                of the last bet or raise
            current_player: an integer representing the first player who has to
                show down.

    Effects:
        prints to 'output_string'
    """
    global output_string
    
    players_in_hand = [True] * len(players) # player hasn't folded yet

    # amount put into pot by each player over all rounds of betting
    wagered_total = [0] * len(players)
    
    for round in range(len(actions_by_round)): # rounds of betting
        if round == 1:
            output_string += "*** FLOP *** ["
            output_string += (board_cards[0][0:2] + " " + board_cards[0][2:4] +
                              " " + board_cards[0][4:6] + "]\n")
        elif round == 2:
            output_string += "*** TURN *** ["
            output_string += (board_cards[0][0:2] + " " + board_cards[0][2:4] +
                              " " + board_cards[0][4:6] + "]")
            output_string += " [" + board_cards[1][0:2] + "]\n"
        elif round == 3:
            output_string += "*** RIVER *** ["
            output_string += (board_cards[0][0:2] + " " + board_cards[0][2:4] +
                              " " + board_cards[0][4:6] + "]")
            output_string += " [" + board_cards[1][0:2] + "]"
            output_string += " [" + board_cards[2][0:2] + "]\n"
            
        # this is a list of lists representing each action in a particular
        # round as a separate list.  In the case of no-limit bets and
        # raises, it will contains two entries, the action and the size.
        actions_this_round = []
        
        if game_type == 'L':
            for action in actions_by_round[round]:
                actions_this_round.append([action])
        else:
            i = 0
            while i < len(actions_by_round[round]):
                if not actions_by_round[round][i] == 'r':
                    actions_this_round.append([actions_by_round[round][i]])
                    i += 1
                else:
                    i += 1
                    bet_size = 0
                    while actions_by_round[round][i].isdigit():
                        bet_size = (bet_size * 10 +
                                    int(actions_by_round[round][i]))
                        i += 1
                    actions_this_round.append(['r', bet_size])

        # amount put into pot by each player in current round
        wagered_this_round = [0] * len(players)
        
        if round == 0:           
            startingPlayer = positions['utg']
            bet_this_round = big_blind
            wagered_this_round[positions['small blind']] += int(big_blind / 2)
            wagered_this_round[positions['big blind']] += big_blind
        else:
            # heads-up reversed blinds
            if len(players) == 2:
                startingPlayer = positions['big blind']
            else:
                startingPlayer = positions['small blind']
            bet_this_round = 0

        if game_type == 'L':
            # preflop or flop
            if round == 0 or round == 1:
                current_bet = big_blind
            else:
                current_bet = big_blind * 2
        else:
            if round == 0:
                current_bet = big_blind
            else:
                current_bet = 0
                    
        current_player = startingPlayer

        # run through all of the actions in the current round
        for actionIndex in range(len(actions_this_round)):

            # index 0 is always a letter (f, c, or r)
            action = actions_this_round[actionIndex][0]

            # get player who matches above action
            while not players_in_hand[current_player]:
                current_player = (current_player + 1) % len(players)

            amountToCall = bet_this_round - wagered_this_round[current_player]
            
            # execute action, record state, and write string
            if action == 'f':
                players_in_hand[current_player] = False
                output_string += players[current_player] + ": folds\n"
            elif action == 'c': # this is either check or call
                if amountToCall == 0: # check
                    output_string += players[current_player] + ": checks\n"
                else: # call
                    wagered_this_round[current_player] += amountToCall
                    output_string += (players[current_player] +
                                      ": calls $" + str(amountToCall) + "\n")
            # this is either bet or raise; for no-limit, we look at index 1
            elif action == 'r':
                if game_type == 'N':
                    current_bet = (actions_this_round[actionIndex][1] -
                                   wagered_total[current_player] -
                                   wagered_this_round[current_player] -
                                   amountToCall)
                wagered_this_round[current_player] += (amountToCall +
                                                      current_bet)
                bet_this_round += current_bet 

                # normal raise or preflop big blind option raise
                if amountToCall > 0 or round == 0:
                    output_string += (players[current_player] +
                                      ": raises $" + str(amountToCall +
                                      current_bet))
                    output_string += " to $" + str(bet_this_round) + "\n"
                else: # bet
                    output_string += (players[current_player] +
                                      ": bets $" + str(current_bet) +
                                      "\n")

            # move to next player
            current_player = (current_player + 1) % len(players)

            while not players_in_hand[current_player]:
                current_player = (current_player + 1) % len(players)

        for i in range(len(players)):
            wagered_total[i] += wagered_this_round[i]
    
    showdown_state = (players_in_hand, wagered_total, current_bet,
                      current_player)

    return showdown_state

def award_pot(hole_cards, results, players, seat_names, positions,
             players_in_hand, wagered_total, current_bet, current_player):
    """Finishes the output string with pot and showdown details
    
    Args:
        hole_cards: A list of strings containing the players' hole cards
        board_cards: A list of strings containing the board cards by street
        results: A list of floats containing the players' monetary results
        players: A list of strings containing the players' names
        seat_names: A list of strings dictating the players' seat assignments
        positions: A dictionary mapping the supported positions to their order
            within the fields of the input file
        players_in_hand: A list of bools representing which players haven't
            folded yet.
        wagered_total: A list of integers denoting how much each
            player has put into the pot in the current hand.
        current_bet: An integer denoting the incremental additional amount of
            the last bet or raise
        current_player: an integer representing the first player who has to
            show down.
    
    Returns:
        None

    Effects:
        prints to 'output_string'
    """
    global output_string
    
    players_left = sum(players_in_hand)
        
    # compute Pot size and Split Pot size
    pot = sum(wagered_total)

    half_pot = float(pot) / 2
    third_pot = pot / 3

    # determine number of winners (multiple if pot is split)
    winners = []
    for i in range(len(players)):
        if float(results[i]) > 0:
            winners.append([i, players[i]])
            
    if players_left > 1:
        output_string += "*** SHOW DOWN ***\n"       
        for i in range(len(players)):
            if players_in_hand[(current_player + i) % len(players)]:
                output_string += (players[(current_player + i) % len(players)] +
                              ": shows [")
                output_string += (hole_cards[(current_player + i) %
                                         len(players)][0:2] + " " +
                              hole_cards[(current_player + i) %
                                         len(players)][2:4] + "]\n")
        if len(winners) == 1:
            output_string += (winners[0][1] + " collected $" + str(pot) +
                          " from pot\n")
        elif len(winners) == 2:
            for winner in winners:
                output_string += (winner[1] + " collected $" +
                              str(round(half_pot, 2)) + " from pot\n")
        elif players_left == 3:
            for i in range(len(players)):
                output_string += (players[i] + " collected $" +
                              str(third_pot) + " from pot\n")
        else: # blinds chop the pot with no profit
            output_string += (players[positions['small blind']] +
                              " collected $" + str(round(half_pot, 2)) +
                              " from pot\n")
            output_string += (players[positions['big blind']] +
                              " collected $" + str(round(half_pot, 2)) +
                              " from pot\n")
    else:
        pot -= current_bet
        output_string += ("Uncalled bet ($" + str(current_bet) +
                          ") returned to " + winners[0][1] + '\n')
        output_string += (winners[0][1] + " collected $" + str(pot) +
                          " from pot")

    final_word = ['mucked'] * len(players)
    if len(winners) == 1:
        final_word[winners[0][0]] = 'won ($' + str(pot) + ')'
    elif len(winners) == 2:
        for winner in winners:
            final_word[winner[0]] = 'won ($' + str(round(half_pot)) + ')'
    elif players_left == 3:
        for i in range(len(players)):
            final_word[i] = 'won ($' + str(third_pot) + ')'
    else:
        final_word[positions['small blind']] = ('won ($' +
                                                str(round(half_pot, 2)) + ')')
        final_word[positions['big blind']] = ('won ($' +
                                              str(round(half_pot, 2)) + ')')


    output_string += "\n*** SUMMARY ***\n"
    output_string += "Total pot $" + str(pot) + "\n"

    if len(players) == 2:
        for i in range(len(players)):
            for j in range (len(players)):
                if seat_names[i] == players[j]:
                    for positions_name, positions_value in positions.items():
                        if (positions_value == j and
                            (positions_name == 'small blind' or
                             positions_name == 'big blind')):
                            output_string += ("Seat " + str(i + 1) + ": " +
                                              seat_names[i] + " (" +
                                              positions_name + ") " +
                                              final_word[j] + '\n')
    else:
        for i in range(len(players)):
            for j in range (len(players)):
                if seat_names[i] == players[j]:
                    for positions_name, positions_value in positions.items():
                        if (positions_value == j and
                            (positions_name == 'small blind' or
                             positions_name == 'big blind' or
                            positions_name == 'button')):
                            output_string += ("Seat " + str(i + 1) + ": " +
                                              seat_names[i] + " (" +
                                              positions_name + ") " +
                                              final_word[j] + '\n')
    output_string += "\n\n\n"                
    

if __name__ == "__main__":
    main(sys.argv[1:])
