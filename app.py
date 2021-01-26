from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
import os, sys, requests

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
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'usertype': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'avatarlink': fields.String
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

class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        id = int(requests.get(f"{api_url}/users/count").text)
        parser.add_argument('username')
        parser.add_argument('usertype')
        parser.add_argument('firstname')
        parser.add_argument('lastname')
        parser.add_argument('avatarlink')
        args = parser.parse_args()
        username = args['username']
        usertype = args['usertype']
        firstname = args['firstname']
        lastname = args['lastname']
        avatarlink = args['avatarlink']
        if (avatarlink == ''):
            avatarlink = 'https://www.jennstrends.com/wp-content/uploads/2013/10/bad-profile-pic-2-768x768.jpeg'
        engine.execute(f"""INSERT INTO Users (id, username, usertype, firstname, lastname, avatarlink) 
                        VALUES ({id}, '{username}', '{usertype}', '{firstname}', '{lastname}', '{avatarlink}');""")

# ENDPOINTS -----------------------------------------------------------------

# GET
api.add_resource(GetAllUsers, "/users")
api.add_resource(GetUserByID, "/users/<int:user_id>")
api.add_resource(GetUserByUsername, "/users/<string:username>")
api.add_resource(GetUserCount, "/users/count")

# POST
api.add_resource(CreateUser, "/users/create-user")

if (__name__) == "__main__":
    app.run(debug=False)
