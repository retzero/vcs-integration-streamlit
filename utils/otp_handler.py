import random
import string
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_otp():
    otp = ''.join(random.choices(string.digits, k=4))
    return otp
