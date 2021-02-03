from flask import Flask, Response
from flask_restful import Api, Resource, fields, marshal_with, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os, sys, requests, json
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_mail import Mail, Message
from scripts import Helper

api_url = 'https://appdomainteam3api.herokuapp.com'
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
    'reactivate_user_date': fields.String
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
            abort(404, message="404 user not found")
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
            abort(404, message="404 user not found")
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
            abort(404, message="404 user not found")
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

class GetHashedPassword(Resource):
    @marshal_with(resource_fields)
    def get(self, hashed_password):
        resultproxy = engine.execute(f"select * from Users where hashed_password = '{hashed_password}'")
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
            abort(404, message="404 password not found")
        return a

class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        id = int(requests.get(f"{api_url}/users/count").text)
        parser.add_argument('email')
        parser.add_argument('usertype')
        parser.add_argument('firstname')
        parser.add_argument('lastname')
        parser.add_argument('avatarlink')
        args = parser.parse_args()
        email = args['email']
        usertype = args['usertype']
        firstname = args['firstname']
        lastname = args['lastname']
        time = datetime.now()
        year = time.strftime("%Y")[2:4]
        month = time.strftime("%m")
        username = firstname[0].lower() + lastname.lower() + month + year
        avatarlink = args['avatarlink']
        if (avatarlink == ''):
            avatarlink = 'https://www.jennstrends.com/wp-content/uploads/2013/10/bad-profile-pic-2-768x768.jpeg'
        password = Helper.GeneratePassword()
        hashed_password = generate_password_hash(password)
        engine.execute(f"""INSERT INTO Users (id, username, email, usertype, firstname, lastname, avatarlink, is_active, is_password_expired, reactivate_user_date, hashed_password) 
                        VALUES ({id}, '{username}', '{email}','{usertype}', '{firstname}', '{lastname}', '{avatarlink}', 1, 0, '1900-01-01', '{hashed_password}');""")
        msg = Message('Hello from appdomainteam3!', recipients=[email])
        msg.body = f"Hello, your login for appdomainteam3 is:\nUsername: {username}\nPassword: {password}"
        mail.send(msg)
        

class NewAccount(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        id = int(requests.get(f"{api_url}/users/count").text)
        parser.add_argument('email')
        parser.add_argument('firstname')
        parser.add_argument('lastname')
        parser.add_argument('avatarlink')
        parser.add_argument('password')
        args = parser.parse_args()
        email = args['email']
        usertype = 'regular_user'
        firstname = args['firstname']
        lastname = args['lastname']
        password = args['password']
        hashed_password = generate_password_hash(password)
        time = datetime.now()
        year = time.strftime("%Y")[2:4]
        month = time.strftime("%m")
        username = firstname[0].lower() + lastname.lower() + month + year
        avatarlink = args['avatarlink']
        if (avatarlink == ''):
            avatarlink = 'https://www.jennstrends.com/wp-content/uploads/2013/10/bad-profile-pic-2-768x768.jpeg'
        engine.execute(f"""INSERT INTO Users (id, username, email, usertype, firstname, lastname, avatarlink, is_active, 
                                              is_password_expired, reactivate_user_date, hashed_password) 
                        VALUES ({id}, '{username}', '{email}','{usertype}', '{firstname}', '{lastname}', '{avatarlink}', 1, 0, '1900-01-01', '{hashed_password}');""")

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
        engine.execute(f"UPDATE Users SET email = '{email}', usertype = '{usertype}', firstname = '{firstname}', lastname = '{lastname}', avatarlink = '{avatarlink}', is_active = '{active}', reactivate_user_date = '{reactivateUserDate}' WHERE id = '{user_id}';")
        response = Response(f"'{username}' updated\n" + json.dumps(args), status=200, mimetype='application/json')
        return response

# ENDPOINTS -----------------------------------------------------------------

# GET
api.add_resource(GetAllUsers, "/users")
api.add_resource(GetHashedPassword, "/users/<string:hashed_password>")
api.add_resource(GetUserByID, "/users/<int:user_id>")
api.add_resource(GetUserByUsername, "/users/<string:username>")
api.add_resource(GetUserCount, "/users/count")

# POST
api.add_resource(CreateUser, "/users/create-user")
api.add_resource(NewAccount, "/users/new-account")
api.add_resource(EditUser, "/users/<int:user_id>/edit")

if (__name__) == "__main__":
    app.run(debug=False)
