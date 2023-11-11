import stripe
from os import getenv
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = getenv("SECRET_STRIPE")
