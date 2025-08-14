import secrets
import string
import uuid


def gen_uuid():
    return str(uuid.uuid4())


MIN_PASS_LEN = 8


def gen_password(length=16):
    if length < MIN_PASS_LEN:
        raise ValueError("Length must be at least {} to include variety of characters".format(MIN_PASS_LEN))

    all_characters = string.ascii_letters + string.digits + string.punctuation
    password = [secrets.choice(string.ascii_lowercase),
                secrets.choice(string.ascii_uppercase),
                secrets.choice(string.digits),
                secrets.choice(string.punctuation)]
    password += [secrets.choice(all_characters) for _ in range(length - MIN_PASS_LEN)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)
