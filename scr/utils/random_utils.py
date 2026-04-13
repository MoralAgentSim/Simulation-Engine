import random
from datetime import datetime

shared_random = random.Random(43)

def set_random_seed(seed: int) -> None:
    """Set the random seed for reproducible results."""
    global shared_random
    shared_random = random.Random(seed)

def get_random_seed() -> int:
    return shared_random.getstate()

def random_choice(choices: list) -> any:
    return shared_random.choice(choices)

def random_choices(choices: list, k: int) -> list:
    return shared_random.choices(choices, k=k)