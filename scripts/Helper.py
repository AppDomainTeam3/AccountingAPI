import random

def GeneratePassword():
    password = ''
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    specials = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    password += random.choice(letters)
    password += random.choice(specials)
    password += str(random.randrange(000000, 999999))
    return password