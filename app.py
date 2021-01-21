from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
import os, sys

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

api.add_resource(GetAllUsers, "/users")
api.add_resource(GetUserByID, "/users/<int:user_id>")
api.add_resource(GetUserByUsername, "/users/<string:username>")

if (__name__) == "__main__":
    app.run(host='127.0.0.2', debug=False)
