# utils/helpers.py
import random
import string
import config

def generate_random_mailbox(prefix_len=config.MAILBOX_PREFIX_LEN, domain=config.MAIL_DOMAIN):
    prefix = ''.join(random.choices(string.ascii_lowercase, k=prefix_len))
    return f"{prefix}test@{domain}"

def generate_random_name(first_len=config.FIRSTNAME_LEN, last_len=config.LASTNAME_LEN):
    first = ''.join(random.choices(string.ascii_letters, k=first_len)).capitalize()
    last = ''.join(random.choices(string.ascii_letters, k=last_len)).capitalize()
    return first, last
