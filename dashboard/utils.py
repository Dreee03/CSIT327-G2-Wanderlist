import random
import datetime

QUOTES = [
    "Travel far enough, you meet yourself.",
    "Not all who wander are lost.",
    "Jobs fill your pocket, adventures fill your soul.",
    "Life is short. Travel often.",
    "Wherever you go becomes part of you.",
]

def get_daily_quote():
    today = datetime.date.today().isoformat()
    seed = hash(today)
    random.seed(seed)
    return random.choice(QUOTES)
