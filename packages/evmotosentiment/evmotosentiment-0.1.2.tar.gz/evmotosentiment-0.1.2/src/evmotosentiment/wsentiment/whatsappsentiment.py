# Single-word entries
WORD_LEXICON = {
    'asleep': -1,
    'reassign': -1,
    'assigning': -1,
    'slot': -1,
    'one': -1,
    'two': -1,
    'single': -1,
    'unlock': -1,
    'no': -1,
    'run': -1,
    'blinking': -1,
    'blink': -1,
    'working': 1,
    'lights': 1,
    'coming': 1,
    'light': 1,
    'bike': 1,
    'turn': 1,
    'on': 1,
    'turning': 1,
    'responding': 1,
    'talking': 1,
    'charging': 1,
    'finished': -1,
    'off': -1,
    "can't": -1,
    "angry": -1,
    'not': -1,
    'out': -1,
    'breaker': -1,
    'breakers': -1,
    'down': -1,
    'shutting': -1,
    'shut': -1,
    'stuck': -1,
    'stucked': -1,
    'back' : 1,
    'solved' : 1,
    'resolved' : 1,
    'prepaid' : 1,
    'restored' : 1,
    'late' : 1,
    'drain' : -1,
    'drained' : -1,
    'draining' : -1,
    'wait': -1,
    'bought': -1,
    'check': -1,
    'reset': -1,
    'waiting': -1,
    'raining': -1,
    'restart': -1,
    'parking': -1,
    'error': -1,
    'manual': -1,
    'depleted': -1,
    'damage': -1,
    'damaged': -1,
    'connector' : -1,
}

# Multi-word (phrase) entries
PHRASE_LEXICON = {
    'lights out': -2,
    'network problems': -2,
    'network problem': -2,
    'light out': -2,
    'not talking': -2,
    'no feedback': -2,
    'not responding': -2,
    'lights off': -2,
    'light off': -2,
    'lights on': 2,
    'light on': 2,
    'light back': 2,
    'not coming on': -2,
    'no power': -2,
    "don't swap": -2,
    'going off': -2,
    'system down': -2,
    'out of fully charged batteries': -2,
    'out of fully': -2,
    'on time': 2,
    'not charging' : -2,
    'not showing' : -2,
    'not publishing' : -2,
    'goes off' : -2,
    'no sound' : -2,
    'open slot' : -2,
    'prepaid finished' : -2,
    'not starting' : -2
}


def wsentiment_score(text):
    """Score the text

    Parameters
    ----------
    text : str
        a pre-processed string without punctuations
        

    Returns
    -------
    score : int
        an integer showing sentence score

    """
    score = 0
    # Match multi-word phrases first
    for phrase, val in PHRASE_LEXICON.items():
        if phrase in text:
            score += val
            # Remove the phrase so it's not double-counted as individual words
            text = text.replace(phrase, '')

    # Score remaining words
    for word in text.split():
        score += WORD_LEXICON.get(word, 0)

    return score