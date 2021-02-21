from flask_restful import fields

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

event_fields = {
    'EventID': fields.Integer,
    'SessionUserID': fields.Integer,
    'UserID': fields.Integer,
    'AccountNumber': fields.Integer,
    'Event': fields.String,
    'Amount': fields.Float,
    'Timestamp': fields.String
}