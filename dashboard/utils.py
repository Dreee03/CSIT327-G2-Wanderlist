import datetime
import hashlib
import random
from wanderlist.quotes import QUOTES

def get_daily_quote():
    """Returns a deterministic quote for the current day."""
    if not QUOTES:
        return "Travel is the only thing you buy that makes you richer."

    today = datetime.date.today().isoformat()
    # Use MD5 hash to ensure the quote is the same for everyone on the same day
    hash_value = int(hashlib.md5(today.encode()).hexdigest(), 16)
    index = hash_value % len(QUOTES)
    return QUOTES[index]

def get_random_quote():
    """Returns a random quote for the refresh button."""
    if not QUOTES:
        return "Adventure is worthwhile."
    return random.choice(QUOTES)