from flask import Response
import random, json

def GeneratePassword():
    password = ''
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    specials = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    password += random.choice(letters)
    password += random.choice(specials)
    password += str(random.randrange(000000, 999999))
    return password

def CustomResponse(status_code, message):
    data = {'status': status_code, 'message': message}
    return Response(json.dumps(data), status=status_code, mimetype='application/json')