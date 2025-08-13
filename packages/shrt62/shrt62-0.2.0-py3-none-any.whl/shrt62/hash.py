#!/usr/bin/env python3
"""Hashing utility for generating unique IDs in base62 format."""
import time
from datetime import datetime
import pytz
import random

class Generator:
    """Utility class for generating unique IDs in base62 format."""
    BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    counter = 0
    last_mill = None

    def __init__(self, timezone="UTC"):
        """Initialize the Generator."""
        self.timezone = pytz.timezone(timezone)


    def encode_base62(self, num):
        """Encodes a number into a base62 string."""
        base_chars = self.BASE62_CHARS

        if num == 0:
            return "0"
        base62 = ""
        while num > 0:
            num, rem = divmod(num, 62)
            base62 = base_chars[rem] + base62
        return base62
    
    def get_current_millis(self):
        """Get current timestamp in milliseconds (adjusted to timezone)."""
        dt = datetime.now(self.timezone)
        return int(dt.timestamp() * 1000)


    def gen(self, length=9):
        """Generates a unique ID based on the current time and a counter."""
        if not (6 <= length <= 9):
            raise ValueError("Length must be between 6 and 9")
        Generator.counter += 1
        if not Generator.last_mill:
            Generator.last_mill = self.get_current_millis()
        current_millis = self.get_current_millis()

        if current_millis != Generator.last_mill:
            Generator.counter = 0
            Generator.last_mill = current_millis          
        timestamp = int(time.time() * 1000)
        Generator.counter += random.randint(1,4)
        unique_number = timestamp * 1000 + Generator.counter
        token = self.encode_base62(unique_number)
        if (length < 9):
            token = token[-length:]
        return token

    @staticmethod
    def generate(length=9):
        """Static method to generate a unique ID."""
        generator = Generator()
        return generator.gen(length=length)


if __name__ == "__main__":
    # Example usage
    unique_id = Generator.generate()
    print(f"Generated unique ID: {unique_id}")
    for i in range(5):
        print(Generator.generate(6))
