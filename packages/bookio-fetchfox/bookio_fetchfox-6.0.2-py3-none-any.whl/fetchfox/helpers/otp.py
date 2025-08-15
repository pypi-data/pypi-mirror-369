import random


def generate_otp(k: int = 6) -> int:
    return int("".join(map(str, random.sample(range(1, 10), k=k))))
