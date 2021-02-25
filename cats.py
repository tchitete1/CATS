"""Typing test implementation"""

from utils import *
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########


def choose(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns true. If there are fewer than K such paragraphs, return
    the empty string.
    """
    selected = []
    for p in paragraphs:
        if select(p): # Check if P should be selected based on SELECT predicate
            selected.append(p)
    
    try: # Item at index K exists
        return selected[k]
    except IndexError as e: # Index K is out of bounds for SELECTED 
        return '' 


def about(topic):
    """Return a select function that returns whether a paragraph contains one
    of the words in TOPIC.

    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'
    def predicate(paragraph):
        paragraph = remove_punctuation(lower(paragraph))
        for t in topic: 
            # Separate str into list of clauses separated by whitespace chars
            for w in split(paragraph): 
                if t == w:
                    return True
        return False 
    return predicate


def accuracy(typed, reference):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of REFERENCE that was typed.

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    """
    # Separate strs into lists of clauses separated by whitespace chars
    typed, reference = split(typed), split(reference)
    correct_words = 0
    total_words = len(typed)
    for i in range(len(reference)):
        try:
            if typed[i] == reference[i]:
                correct_words += 1
        except IndexError as e:
            pass
   
    percentage = 0.0 # Safety against ZeroDivison errors 
    if total_words != 0: # TYPED isn't an empty string 
        percentage = (correct_words / total_words) * 100.0
    return percentage 


def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string.
        
    NOTE: Despite its name, words per minute is not based on the number of words
    typed, but instead the number of characters, so that a typing test is not
    biased by the length of words. The formula for words per minute is the ratio
    of the number of of characters (including spaces) typed divided by 5 (a 
    typical word length) to the elapsed time in minutes."""

    assert elapsed > 0, 'Elapsed time must be positive'
    typical_word_length = 5
    num_words_typed = len(typed) / typical_word_length
    min_as_sec = 60
    elapsed_as_mins = elapsed / min_as_sec
    return num_words_typed / elapsed_as_mins


def autocorrect(user_word, valid_words, diff_function, limit):
    """Returns the element of VALID_WORDS that has the smallest difference
    from USER_WORD. Instead returns USER_WORD if that difference is greater
    than LIMIT.
    """
    if user_word in valid_words: # User typed word correctly
        return user_word

    diffs = []  
    for x in valid_words:
        # Find out distance between USER_WORD and current word in VALID_WORDS
        d = diff_function(user_word, x, limit)
        diffs.append(d)

    # Closest word gotten from VALID_WORDS is too far from USER_WORDS
    if min(diffs) > limit:
        return user_word
    else:
        # Get index of word and word in VALID_WORDS closest to USER_WORD
        closest_index = diffs.index(min(diffs))
        closest = valid_words[closest_index]
        return closest


def shifty_shifts(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths.
    """
    if start == goal: # Initial or remaining stings are identical
        return 0
    elif limit == 0: # Ensure recursion stops once limit is reached 
        return limit + 1 
    elif "" in (start, goal): 
        return abs(len(start) - len(goal)) # Number of missing/extra chars 
    elif start[0] == goal[0]: # No substitution
        return 0 + shifty_shifts(start[1:], goal[1:], limit)
    else: # Substitution
        return 1 + shifty_shifts(start[1:], goal[1:], limit - 1)

def meowstake_matches(start, goal, limit):
    """A diff function that computes the edit distance from START to GOAL."""

    if start == goal: # Initial or remaining strings are identical
        return 0
    elif limit == 0: # Ensure recursion stops once limit is reached
        return limit + 1
    elif "" in (start, goal):
        return abs(len(start) - len(goal)) # Represents additional operations
    elif start[0] == goal[0]: # No edit operation
        return 0 + meowstake_matches(start[1:], goal[1:], limit)
    else:
        add_diff = meowstake_matches(start, goal[1:], limit - 1) 
        rem_diff = meowstake_matches(start[1:], goal, limit - 1)
        sub_diff = meowstake_matches(start[1:], goal[1:], limit - 1)
        return 1 + min(add_diff, rem_diff, sub_diff)

def final_diff(start, goal, limit):
    """A diff function. If you implement this function, it will be used."""
    assert False, 'Remove this line to use your final_diff function.'

###########
# Phase 3 #
###########


def report_progress(typed, prompt, id, send):
    """Send a report of your id and progress so far to the multiplayer server."""
    i = 0
    correct_words = 0
    total_words = len(prompt)
    correct = True
    # Count number of words user has typed correctly
    while (i < len(typed)) and correct:
        if typed[i] == prompt[i]: # Word typed is correct
            correct_words += 1  
        else:
            correct = False
        i += 1
    ratio = correct_words / total_words
    # Send progress report to multiplayer server
    send({'id': id, 'progress': ratio}) 
    return ratio
            

def fastest_words_report(times_per_player, words):
    """Return a text description of the fastest words typed by each player."""
    game = time_per_word(times_per_player, words)
    fastest = fastest_words(game)
    report = ''
    for i in range(len(fastest)):
        words = ','.join(fastest[i])
        report += 'Player {} typed these fastest: {}\n'.format(i + 1, words)
    return report


def time_per_word(times_per_player, words):
    """Given timing data, return a game data abstraction, which contains a list
    of words and the amount of time each player took to type each word.

    Arguments:
        times_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time
                          the player finished typing each word.
        words: a list of words, in the order they are typed.
    """
    time_diffs_for_player = [] # Each player
    time_diffs_per_player = [] # All players
    # Loop through all times in TIMES_PER_PLAYER
    for i in range(len(times_per_player)):
        # Loop through all times to calculate TIME_DIFFS for player
        for j in range(1, len(times_per_player[0])):
            time_diffs_for_player.append(times_per_player[i][j] - \
                                         times_per_player[i][j - 1])
        time_diffs_per_player.append(time_diffs_for_player)
        time_diffs_for_player = []
    return game(words, time_diffs_per_player)


def fastest_words(game):
    """Return a list of lists of which words each player typed fastest.

    Arguments:
        game: a game data abstraction as returned by time_per_word.
    Returns:
        a list of lists containing which words each player typed fastest
    """
    players_indexes = range(len(all_times(game)))  # An index for each player
    words_indexes = range(len(all_words(game)))    # An index for each word
    
    # Creates mapping between words and players, with times as elements
    words_to_players = []
    times_for_word = []
    times = all_times(game)
    for w_i in words_indexes:
        for p_i in players_indexes:
            times_for_word.append(times[p_i][w_i])
        words_to_players.append(times_for_word)
        times_for_word = []

    # Uses mapping to find player that typed each word the fastest
    fastest_players = []
    for ws in words_to_players:
        fastest_players.append(ws.index(min(ws)))
    print("Debug: fastest_players =", fastest_players)

    # Creates list of lists of words each player typed the fastest
    words = all_words(game)    
    players_to_words = []
    words_for_player = []
    for p_i in players_indexes:
        for w_i in words_indexes:
            print("Debug: ", fastest_players[w_i])
            # Current word was typed fastest by current player
            if fastest_players[w_i] == p_i:
                words_for_player.append(words[w_i]) 
        print("Debug: words_for_player =", words_for_player)
        players_to_words.append(words_for_player)
        words_for_player = []
    return players_to_words 

def game(words, times):
    """A data abstraction containing all words typed and their times."""
    assert all([type(w) == str for w in words]), 'words should be a list of strings'
    assert all([type(t) == list for t in times]), 'times should be a list of lists'
    assert all([isinstance(i, (int, float)) for t in times for i in t]), 'times lists should contain numbers'
    assert all([len(t) == len(words) for t in times]), 'There should be one word per time.'
    return [words, times]


def word_at(game, word_index):
    """A selector function that gets the word with index word_index"""
    assert 0 <= word_index < len(game[0]), "word_index out of range of words"
    return game[0][word_index]


def all_words(game):
    """A selector function for all the words in the game"""
    return game[0]


def all_times(game):
    """A selector function for all typing times for all players"""
    return game[1]


def time(game, player_num, word_index):
    """A selector function for the time it took player_num to type the word at word_index"""
    assert word_index < len(game[0]), "word_index out of range of words"
    assert player_num < len(game[1]), "player_num out of range of players"
    return game[1][player_num][word_index]


def game_string(game):
    """A helper function that takes in a game object and returns a string representation of it"""
    return "game(%s, %s)" % (game[0], game[1])

enable_multiplayer = False  # Change to True when you

##########################
# Extra Credit #
##########################

key_distance = get_key_distances()
def key_distance_diff(start, goal, limit):
    """ A diff function that takes into account the distances between keys when
    computing the difference score."""

    start = start.lower() #converts the string to lowercase
    goal = goal.lower() #converts the string to lowercase

    # BEGIN PROBLEM EC1
    "*** YOUR CODE HERE ***"
    # END PROBLEM EC1

def memo(f):
    """A memoization function as seen in John Denero's lecture on Growth"""

    cache = {}
    def memoized(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memoized

key_distance_diff = count(key_distance_diff)


def faster_autocorrect(user_word, valid_words, diff_function, limit):
    """A memoized version of the autocorrect function implemented above."""

    # BEGIN PROBLEM EC2
    "*** YOUR CODE HERE ***"
    # END PROBLEM EC2


##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        reference = choose(paragraphs, select, i)
        if not reference:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(reference)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, reference))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
