import datetime
import jwt
from flask import current_app

def generate_token(user_id, active_role):
    payload = {
        "user_id": user_id,
        "active_role": active_role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
