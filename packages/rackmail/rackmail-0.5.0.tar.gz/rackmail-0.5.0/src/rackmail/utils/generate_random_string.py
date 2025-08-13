import string
import random

def generate_random_string(length=16) -> str:
    """Generates a random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))