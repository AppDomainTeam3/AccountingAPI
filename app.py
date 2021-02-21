from flask import Flask, Response, request
from flask_restful import Api, Resource, fields, marshal_with, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os, sys, requests, json
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from scripts import Helper

api_url = 'http://127.0.0.2:5000'
server = 'AppDomainTeam3.database.windows.net'
database = 'AppDomainTeam3'
username = os.environ.get('sql_username')
password = os.environ.get('sql_password')
driver= 'ODBC+Driver+17+for+SQL+Server'
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
engine = SQLAlchemy.create_engine(SQLAlchemy, connection_string, {})

try:
    connection = engine.connect()
except Exception as ex:
    print('Database connection FAILED!:')
    print(ex)
    sys.exit()

app = Flask(__name__)
app.config.from_object("config.DevelopementConfig")
app.config['SQLALCHEMY_DATABASE_URI'] = server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
mail = Mail(app)
CORS(app)
api = Api(app)

resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'usertype': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'avatarlink': fields.String,
    'hashed_password': fields.String,
    'is_active': fields.String,
    'is_password_expired': fields.String,
    'reactivate_user_date': fields.String,
    'failed_login_attempts': fields.Integer,
    'password_expiration_date': fields.String
}

account_fields = {
    'id':  fields.Integer,
    'AccountName': fields.String,
    'AccountNumber': fields.Integer,
    'AccountDesc': fields.String,
    'NormalSide': fields.String,
    'Category': fields.String,
    'Subcategory': fields.String,
    'Balance': fields.Float,
    'AccountCreationDate': fields.String,
    'AccountOrder': fields.Integer,
    'Statement': fields.String,
    'Comment': fields.String,
    'IsActive': fields.String
}

class GetAllUsers(Resource):
    @marshal_with(resource_fields)
    def get(self):
        resultproxy = engine.execute(f"SELECT * FROM Users ORDER BY id ASC")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(Helper.CustomResponse(404, 'no users found'))
        return a

class GetUserByID(Resource):
    @marshal_with(resource_fields)
    def get(self, user_id):
        resultproxy = engine.execute(f"select * from Users where id = {user_id}")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(Helper.CustomResponse(404, 'user not found with provided id'))
        return a

class GetUserByUsername(Resource):
    @marshal_with(resource_fields)
    def get(self, username):
        resultproxy = engine.execute(f"select * from Users where username = '{username}'")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(Helper.CustomResponse(404, 'user not found with provided username'))
        return a

class GetUserCount(Resource):
    def get(self):
        resultproxy = engine.execute(f"select COUNT(id) from Users")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            # build up the dictionary
            d = {**d, **{"count": rowproxy[0]}}
            a.append(d)
        if not a:
            return 0
        return a[0]['count']

class GetAccounts(Resource):
    @marshal_with(account_fields)
    def get(self, user_id):
        resultproxy = engine.execute(f"SELECT * FROM Accounts where id = {user_id} ORDER BY id ASC")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(404, message="404 Account not found")
        return a

class GetAccountByAccountNumber(Resource):
    @marshal_with(account_fields)
    def get(self, account_number):
        resultproxy = engine.execute(f"SELECT * FROM Accounts where AccountNumber = {account_number} ORDER BY id ASC")
        d = {}
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
        if not d:
            abort(Helper.CustomResponse(404, 'account not found with provided account number'))
        return d

class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        id = int(requests.get(f"{api_url}/users/count").text)
        parser.add_argument('sessionUserID')
        parser.add_argument('form')
        args = parser.parse_args()

        sessionUserID = args['sessionUserID']
        formData = args['form']
        formDict = Helper.ParseArgs(formData)

        try:
            usertype = formDict['usertype'] 
        except:
            usertype = 'regular_user'
        firstname = formDict['firstname']
        lastname = formDict['lastname']
        email = formDict['email']
        time = datetime.now()
        year = time.strftime("%Y")[2:4]
        month = time.strftime("%m")
        username = firstname[0].lower() + lastname.lower() + month + year
        avatarlink = formDict['avatarlink']
        password_expiration_date = time + timedelta(days=7)
        password_Ex = password_expiration_date.strftime('%Y-%m-%d')
        if (avatarlink == ''):
            avatarlink = 'https://www.jennstrends.com/wp-content/uploads/2013/10/bad-profile-pic-2-768x768.jpeg'
        try:
            password = formDict['password']
        except:
            password = Helper.GeneratePassword()

        hashed_password = generate_password_hash(password)
        engine.execute(f"""INSERT INTO Users (id, username, email, usertype, firstname, lastname, avatarlink, is_active, 
                                            is_password_expired, reactivate_user_date, hashed_password, failed_login_attempts, password_expiration_date) 
                        VALUES ({id}, '{username}', '{email}','{usertype}', '{firstname}', '{lastname}', '{avatarlink}', 1, 0, '1900-01-01', '{hashed_password}', 0,'{password_Ex}');
                        INSERT INTO Passwords (id, password) VALUES ({id}, '{hashed_password}');""")

        message = f"User created!"
        data = {'SessionUserID': sessionUserID, 'UserID': id, 'AccountNumber': 0, 'Amount': 0, 'Event': message}
        requests.post(f"{api_url}/events/create", json=data)

        msg = Message('Hello from appdomainteam3!', recipients=[email])
        msg.body = f"Hello, your login for appdomainteam3 is:\nUsername: {username}\nPassword: {password}"
        mail.send(msg)

class CreateAccount(Resource):
    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('accountHolderUsername')
        parser.add_argument('accountName')
        parser.add_argument('accountDesc')
        parser.add_argument('normalSide')
        parser.add_argument('category')
        args = parser.parse_args()
        if args['accountHolderUsername'] != None:
            user = args['accountHolderUsername']
        else:
            user = username
        response = requests.get(f"{api_url}/users/{user}")
        if response.status_code == 404:
            return(response.json())
        user = response.json()[0]
        id = user['id']
        accountName = args['accountName']
        accountDesc = args['accountDesc']
        normalSide = args['normalSide']
        category = args['category']
        subcategory = 'None'
        balance = 0
        creationDate = datetime.now().strftime('%Y-%m-%d')
        accountOrder = 1
        statement = 'None'
        comment = 'None'
        accountNumber = Helper.GenerateAccountNumber()
        isActive = 1

        query = f"""INSERT INTO Accounts VALUES ({id}, '{accountName}', {accountNumber}, '{accountDesc}', '{normalSide}',
                                                            '{category}', '{subcategory}', {balance}, '{creationDate}', {accountOrder},
                                                            '{statement}', '{comment}', {isActive})"""
        try:
            engine.execute(query)
        except Exception as e:
            print(e)
            return Response("SQL Error", status=500, mimetype='application/json')

        email = user['email']
        msg = Message('Account Creation Notice', recipients=[email])
        msg.body = f"Hello,\nThank you for opening a {category} account with us!"
        mail.send(msg)

        response = Helper.CustomResponse(200, 'Account Created!')
        return response

class EditAccount(Resource):
    def post(self, account_number):
        parser = reqparse.RequestParser()
        parser.add_argument('accountName')
        parser.add_argument('accountDesc')
        parser.add_argument('normalSide')
        parser.add_argument('category')
        parser.add_argument('subcategory')
        parser.add_argument('accountOrder')
        parser.add_argument('statement')
        parser.add_argument('comment')
        args = parser.parse_args()

        accountName = args['accountName']
        accountDesc = args['accountDesc']
        normalSide = args['normalSide']
        category = args['category']
        subcategory = args['subcategory']
        accountOrder = args['accountOrder']
        comment = args['comment']

        query = f"""UPDATE Accounts SET AccountName = '{accountName}', AccountDesc = '{accountDesc}', NormalSide = '{normalSide}', Category = '{category}', Subcategory = '{subcategory}', AccountOrder = {accountOrder}, Comment = '{comment}' WHERE AccountNumber = {account_number}"""

        try:
            engine.execute(query)
        except Exception as e:
            print(e)
            return Response("SQL Error", status=500, mimetype='application/json')

        response = Helper.CustomResponse(200, 'Account Edited Successfully!')
        return response

class ToggleAccountActiveStatus(Resource):
    def post(self, account_number):
        response = requests.get(f"{api_url}/accounts/{account_number}")
        if response.status_code == 404:
            return(response.json())
        isActive = response.json()['IsActive']
        query = ''
        if isActive == 'True':
            if response.json()['Balance'] == 0:
                query = f"""UPDATE Accounts SET IsActive = 0 WHERE AccountNumber = {account_number}"""
            else:
                return Helper.CustomResponse(406, 'Balance must be $0.00 to be deactivated')
        else:
            query = f"""UPDATE Accounts SET IsActive = 1 WHERE AccountNumber = {account_number}"""

        try:
            engine.execute(query)
        except Exception as e:
            print(e)
            return Helper.CustomResponse(500, 'SQL Error')
        user = response.json()['id']
        if isActive == 'True':
            message = f"Account {account_number} deactivated!"
            custom_response = Helper.CustomResponse(200, message)
            data = {'id': response.json()['id'], 'AccountNumber': response.json()['AccountNumber'], 'Amount': 0, 'Event': message}
            requests.post(f"{api_url}/events/create", json=data)
            return custom_response
        else:
            message = f"Account {account_number} activated!"
            custom_response = Helper.CustomResponse(200, message)
            data = {'id': response.json()['id'], 'AccountNumber': response.json()['AccountNumber'], 'Amount': 0, 'Event': message}
            requests.post(f"{api_url}/events/create", json=data)
            return custom_response


class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('email')
        args = parser.parse_args()
        username = args['username']
        email = args['email']
        response = requests.get(f"{api_url}/users/{username}")
        if (response.status_code != 200):
            return Response("No user with that username!", status=404, mimetype='application/json')
        if (response.json()[0]['email'] != email):
            return Response(f"Email does not match email on file for {username}!", status=406, mimetype='application/json')
        id = response.json()[0]['id']
        password = Helper.GeneratePassword()
        msg = Message('Hello from appdomainteam3!', recipients=[email])
        msg.body = f"Hello, your login for appdomainteam3 is:\nUsername: {username}\nPassword: {password}"
        mail.send(msg)
        password = generate_password_hash(password)
        engine.execute(f"""UPDATE Users SET hashed_password = '{password}' WHERE id = {id}; INSERT INTO Passwords (id, password) VALUES ({id}, '{password}');""")
        return Response(f"Temporary password sent!", status=200, mimetype='application/json')

class FailedLogin(Resource):
    def post(self, user_id):
        response = requests.get(f"{api_url}/users/{user_id}")
        if (response.status_code == 404):
            return Response("User not found", status = 404, mimetype='application/json')
        if (response.json()[0]['is_active'] == 'False'):
            return Response(f"User is disabled until {response.json()[0]['reactivate_user_date']}", status = 200, mimetype='application/json')
        failed_logins = response.json()[0]['failed_login_attempts']
        reactivateUserDate = datetime.now()
        if (failed_logins >= 2):
            reactivateUserDate = timedelta(days=1) + datetime.now()
            reactivateUserDate = reactivateUserDate.strftime('%Y-%m-%d')
            engine.execute(f"UPDATE Users SET failed_login_attempts = '{failed_logins + 1}', reactivate_user_date = '{reactivateUserDate}', is_active = 0 WHERE id = {user_id};")
        engine.execute(f"UPDATE Users SET failed_login_attempts = '{failed_logins + 1}' WHERE id = {user_id};")

class GetPasswords(Resource):
    def get(self, user_id):
        resultproxy = engine.execute(f"select * from Passwords where id = {user_id}")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(404, message="404 user not found")
        response = Response(json.dumps(a), status=200, mimetype='application/json')
        return response

class TestNewPassword(Resource):
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('currentPassword')
        parser.add_argument('newPassword')
        args = parser.parse_args()
        currentPassword = args['currentPassword']
        newPassword = args['newPassword']
        sqlCurrentPassword = requests.get(f"{api_url}/users/{user_id}").json()[0]['hashed_password']
        previousPasswords = requests.get(f"{api_url}/users/{user_id}/get_passwords").json()
        if (check_password_hash(sqlCurrentPassword, currentPassword) == False):
            response = Response("Incorrect current password!", status=401, mimetype='application/json')
            return response
        for entry in previousPasswords:
            if check_password_hash(entry['password'], newPassword):
                response = Response("New password has been used before!", status=406, mimetype='application/json')
                return response
        newPassword = generate_password_hash(newPassword)
        engine.execute(f"""UPDATE Users SET hashed_password = '{newPassword}' WHERE id = {user_id}; INSERT INTO Passwords (id, password) VALUES ({user_id}, '{newPassword}');""")
        response = Response("Password has been updated!", status=200, mimetype='application/json')
        return response

    def get(self, user_id):
        return Response("Testing!", status=200, mimetype='application/json')

class EditUser(Resource):
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('deactivate')
        parser.add_argument('email')
        parser.add_argument('usertype')
        parser.add_argument('firstname')
        parser.add_argument('lastname')
        parser.add_argument('avatarlink')
        args = parser.parse_args()
        reactivateUserDate = args['deactivate']
        if reactivateUserDate == '':
            reactivateUserDate = '1900-01-01'
        active = False
        if (datetime.strptime(reactivateUserDate, '%Y-%m-%d') < datetime.now()):
            active = True
        email = args['email']
        usertype = args['usertype']
        firstname = args['firstname']
        lastname = args['lastname']
        avatarlink = args['avatarlink']
        if (avatarlink == ''):
            avatarlink = 'https://www.jennstrends.com/wp-content/uploads/2013/10/bad-profile-pic-2-768x768.jpeg'
        engine.execute(f"""UPDATE Users SET email = '{email}', usertype = '{usertype}', firstname = '{firstname}', lastname = '{lastname}',
                           avatarlink = '{avatarlink}', is_active = '{active}', reactivate_user_date = '{reactivateUserDate}' WHERE id = '{user_id}';""")
        response = Response(f"'{username}' updated\n" + json.dumps(args), status=200, mimetype='application/json')
        return response

class CreateEvent(Resource):
    def post(self):
        content = request.get_json()
        creationDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        eventID = requests.get(f"{api_url}/events/count").json()
        query = f"""INSERT INTO Events VALUES ({eventID}, {content['SessionUserID']}, {content['UserID']}, {content['AccountNumber']}, '{content['Event']}', {content['Amount']}, '{creationDateTime}')"""
        try:
            engine.execute(query)
        except Exception as e:
            print(e)
            return Helper.CustomResponse(500, 'SQL Error')

class GetEventCount(Resource):
    def get(self):
        query = "SELECT COUNT(EventID) from Events"
        try:
            resultProxy = engine.execute(query)
        except Exception as e:
            print(e)
            return Helper.CustomResponse(500, 'SQL Error')
        for rowProxy in resultProxy:
            return rowProxy[0]

# ENDPOINTS -----------------------------------------------------------------

# GET
api.add_resource(GetAllUsers, "/users")
api.add_resource(GetUserByID, "/users/<int:user_id>")
api.add_resource(GetUserByUsername, "/users/<string:username>")
api.add_resource(GetUserCount, "/users/count")
api.add_resource(GetPasswords, "/users/<int:user_id>/get_passwords")
api.add_resource(GetAccounts, "/users/<int:user_id>/accounts")
api.add_resource(GetAccountByAccountNumber, "/accounts/<int:account_number>")
api.add_resource(GetEventCount, "/events/count")

# POST
api.add_resource(CreateUser, "/users/create-user")
api.add_resource(EditUser, "/users/<int:user_id>/edit")
api.add_resource(ForgotPassword, "/forgot_password")
api.add_resource(TestNewPassword, "/users/<int:user_id>/test_new_password")
api.add_resource(FailedLogin, "/users/<int:user_id>/failed_login")
api.add_resource(CreateAccount, "/accounts/create/<string:username>")
api.add_resource(EditAccount, "/accounts/<int:account_number>/edit")
api.add_resource(ToggleAccountActiveStatus, "/accounts/<int:account_number>/toggle")
api.add_resource(CreateEvent, "/events/create")

if (__name__) == "__main__":
    app.run(host='127.0.0.2', debug=True)
