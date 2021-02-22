from flask import Response
import random, json, urllib.parse, requests

def GeneratePassword():
    password = ''
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    specials = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    password += random.choice(letters)
    password += random.choice(specials)
    password += str(random.randrange(000000, 999999))
    return password

def GenerateAccountNumber(api_url):
    isGenerating = True
    while isGenerating:
        newAccountNumber = random.randrange(10000000, 99999999)
        response = requests.get(f"{api_url}/accounts/{newAccountNumber}")
        if response.status_code != 404:
            continue
        return newAccountNumber

def CheckForDuplicateAccountName(userID, accountName, api_url):
    response = requests.get(f"{api_url}/users/{userID}/accounts")
    for account in response.json():
        if account['AccountName'] == accountName:
            return CustomResponse(406, 'This user already has an account with the provided name')
    return CustomResponse(200, 'No duplicate found')

def CustomResponse(status_code, message):
    data = {'status': status_code, 'message': message}
    return Response(json.dumps(data), status=status_code, mimetype='application/json')

def ParseArgs(str):
    str = urllib.parse.unquote(str)
    str = str.split("&")
    data = {}
    for split in str:
        split = split.split("=")
        data.update({f"{split[0]}": f"{split[1]}"})
    return data
