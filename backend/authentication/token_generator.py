import random
import string


def generate_token(token_length=6):
    chars = string.ascii_uppercase
    numbers = string.digits
    total_digits = random.choice([num for num in range(token_length - 1)])
    chars_collection = [random.choice(chars) for _ in range(token_length - total_digits)]
    digits_collection = [random.choice(numbers) for _ in range(total_digits)]

    return ''.join(chars_collection + digits_collection)
