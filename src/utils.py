import random
from typing import ClassVar, List
from textwrap import wrap


class PrimeGenerator:
    __PRIMES: ClassVar[List[int]]

    @staticmethod
    def fill() -> None:
        PrimeGenerator.__PRIMES = []
        n = 10000000
        prime = [True] * n
        for i in range(3, int(n ** 0.5) + 1, 2):
            if prime[i]:
                prime[i * i:: 2 * i] = [False] * ((n - i * i - 1) // (2 * i) + 1)

        PrimeGenerator.__PRIMES = [2] + [i for i in range(3, n, 2) if prime[i]]

    @staticmethod
    def random():
        return random.choice(PrimeGenerator.__PRIMES)

    @staticmethod
    def random_above(n):
        filtered_prime = [x for x in PrimeGenerator.__PRIMES if x >= n]
        return random.choice(filtered_prime)

    @staticmethod
    def random_below(n):
        filtered_prime = [x for x in PrimeGenerator.__PRIMES if x <= n]
        selected_prime = random.choice(filtered_prime)
        while (gcd(selected_prime, n) != 1):
            selected_prime = random.choice(filtered_prime)
        return selected_prime


def gcd(a: int, b: int) -> int:
    if a == 0:
        return b
    return gcd(b % a, a)

def hex_to_message(hex: str):
    padding_hex = "0" + hex if (len(hex) % 2 == 1) else hex
    hex_characters = wrap(padding_hex, 2)
    message = ""
    for hex_char in hex_characters:
        message += chr(int(hex_char, 16))
    return message

def message_to_hex(message: str):
    hex_message = ""
    i = 0
    for char in message:
        hex = str(format(ord(char), "02x"))
        # print(char, hex, sep='-', end="\n")
        hex_message += hex
    return hex_message

PrimeGenerator.fill()