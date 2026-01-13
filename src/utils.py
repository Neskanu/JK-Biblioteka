import random
import string

def generate_card_id():
    """
    Sugeneruoja atsitiktinį skaitytojo pažymėjimo ID.
    Formatas: 2 didžiosios raidės + 4 skaičiai (pvz., AB1234).
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}{numbers}"